import sqlite3
import json
import chromadb
from uuid import UUID
from typing import List, Optional, Dict, Any
from src.models.models import Metadata, Note

class DatabaseManager:
    def __init__(self, db_path: str = "vault.db", chroma_path: str = "chroma_data"):
        self.db_path = db_path
        self.chroma_path = chroma_path
        self._init_db()
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
        self.collection = self.chroma_client.get_or_create_collection(
            name="vault_embeddings",
            metadata={"description": "Vector store for SensusVault notes"}
        )

    def _init_db(self):
        conn = sqlite3.connect(self.db_path, timeout=30)
        try:
            with conn:
                cursor = conn.cursor()
                # Notes table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS notes (
                        id TEXT PRIMARY KEY,
                        content TEXT,
                        metadata TEXT,
                        embedding BLOB
                    )
                """)
                # Graph Nodes
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS nodes (
                        id TEXT PRIMARY KEY,
                        type TEXT,
                        metadata TEXT
                    )
                """)
                # Graph Edges
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS edges (
                        source_id TEXT,
                        target_id TEXT,
                        relation_type TEXT,
                        PRIMARY KEY (source_id, target_id, relation_type)
                    )
                """)
                # Action Queue
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pending_actions (
                        id TEXT PRIMARY KEY,
                        type TEXT,
                        payload TEXT,
                        status TEXT,
                        created_at TIMESTAMP
                    )
                """)
        finally:
            conn.close()

    def add_action(self, action: Action):
        conn = sqlite3.connect(self.db_path, timeout=30)
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO pending_actions (id, type, payload, status, created_at) VALUES (?, ?, ?, ?, ?)",
                    (str(action.id), action.type, json.dumps(action.payload), action.status, action.created_at.isoformat())
                )
        finally:
            conn.close()

    def get_pending_actions(self) -> List[Action]:
        conn = sqlite3.connect(self.db_path, timeout=30)
        actions = []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, type, payload, status, created_at FROM pending_actions WHERE status = 'pending'")
            rows = cursor.fetchall()
            for row in rows:
                actions.append(Action(
                    id=UUID(row[0]),
                    type=row[1],
                    payload=json.loads(row[2]),
                    status=row[3],
                    created_at=datetime.fromisoformat(row[4])
                ))
        finally:
            conn.close()
        return actions

    def update_action_status(self, action_id: UUID, status: str):
        conn = sqlite3.connect(self.db_path, timeout=30)
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE pending_actions SET status = ? WHERE id = ?", (status, str(action_id)))
        finally:
            conn.close()

    def execute_action(self, action_id: UUID):
        """
        Executes an approved action and updates its status.
        """
        conn = sqlite3.connect(self.db_path, timeout=30)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT type, payload FROM pending_actions WHERE id = ?", (str(action_id),))
            row = cursor.fetchone()
            if not row:
                return
            
            action_type, payload_json = row
            payload = json.loads(payload_json)
            
            if action_type == "create_note":
                note = Note(
                    content=payload["content"],
                    metadata=Metadata(
                        title=payload["title"],
                        source=payload["source"],
                        tags=payload.get("tags", [])
                    )
                )
                self.insert_note(note)
            elif action_type == "delete_note":
                self.delete_note(UUID(payload["note_id"]))
            elif action_type == "update_metadata":
                note_id = UUID(payload["note_id"])
                self.update_note_metadata(note_id, Metadata(**payload["metadata"]))
            elif action_type == "generate_graph_link":
                self.add_edge(
                    UUID(payload["source_id"]),
                    UUID(payload["target_id"]),
                    payload["relation"]
                )
            
            # Mark as completed
            with conn:
                cursor.execute("UPDATE pending_actions SET status = 'completed' WHERE id = ?", (str(action_id),))
        finally:
            conn.close()

    def delete_note(self, note_id: UUID):
        # Delete from ChromaDB
        self.collection.delete(ids=[str(note_id)])
        
        # Delete from SQLite
        conn = sqlite3.connect(self.db_path, timeout=30)
        try:
            with conn:
                cursor = conn.cursor()
                # Delete from notes
                cursor.execute("DELETE FROM notes WHERE id = ?", (str(note_id),))
                # Delete associated graph nodes (simplified: delete node if it matches ID)
                cursor.execute("DELETE FROM nodes WHERE id = ?", (str(note_id),))
                # Delete edges where this note is source or target
                cursor.execute("DELETE FROM edges WHERE source_id = ? OR target_id = ?", (str(note_id), str(note_id)))
        finally:
            conn.close()

    def insert_note(self, note: Note):
        # Insert into ChromaDB
        if note.embedding:
            self.collection.add(
                ids=[str(note.id)],
                embeddings=[note.embedding],
                metadatas=[{"title": note.metadata.title, "source": note.metadata.source}]
            )

        # Insert into SQLite
        conn = sqlite3.connect(self.db_path, timeout=30)
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO notes (id, content, metadata, embedding) VALUES (?, ?, ?, ?)",
                    (str(note.id), note.content, note.metadata.model_dump_json(), json.dumps(note.embedding) if note.embedding else None)
                )
                # Insert as a node
                self.get_or_create_node(note.id, "note", note.metadata.model_dump_json(), conn=conn)
        finally:
            conn.close()

    def get_or_create_node(self, node_id: UUID, node_type: str, metadata_json: str, conn=None) -> str:
        """
        Gets an existing node ID or creates a new one.
        """
        if conn is None:
            conn = sqlite3.connect(self.db_path, timeout=30)
            try:
                cursor = conn.cursor()
                # Work with cursor...
                cursor.execute("SELECT id FROM nodes WHERE id = ?", (str(node_id),))
                row = cursor.fetchone()
                if row:
                    return row[0]
                else:
                    cursor.execute(
                        "INSERT INTO nodes (id, type, metadata) VALUES (?, ?, ?)",
                        (str(node_id), node_type, metadata_json)
                    )
                    return str(node_id)
            finally:
                conn.close()
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM nodes WHERE id = ?", (str(node_id),))
            row = cursor.fetchone()
            if row:
                return row[0]
            else:
                cursor.execute(
                    "INSERT INTO nodes (id, type, metadata) VALUES (?, ?, ?)",
                    (str(node_id), node_type, metadata_json)
                )
                return str(node_id)

        cursor.execute("SELECT id FROM nodes WHERE id = ?", (str(node_id),))
        row = cursor.fetchone()
        if row:
            return row[0]
        else:
            cursor.execute(
                "INSERT INTO nodes (id, type, metadata) VALUES (?, ?, ?)",
                (str(node_id), node_type, metadata_json)
            )
            return str(node_id)

    def add_edge(self, source_id: UUID, target_id: UUID, relation: str):
        conn = sqlite3.connect(self.db_path, timeout=30)
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO edges (source_id, target_id, relation_type) VALUES (?, ?, ?)",
                    (str(source_id), str(target_id), relation)
                )
        except sqlite3.IntegrityError:
            # Handle duplicate edges gracefully
            pass
        finally:
            conn.close()

    def get_note(self, note_id: UUID) -> Optional[Note]:
        conn = sqlite3.connect(self.db_path, timeout=30)
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("SELECT content, metadata FROM notes WHERE id = ?", (str(note_id),))
                row = cursor.fetchone()
                if row:
                    metadata = Metadata.parse_raw(row[1])
                    return Note(id=note_id, content=row[0], metadata=metadata)
        finally:
            conn.close()
        return None

    def update_note_metadata(self, note_id: UUID, new_metadata: Metadata):
        conn = sqlite3.connect(self.db_path, timeout=30)
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE notes SET metadata = ? WHERE id = ?",
                    (new_metadata.model_dump_json(), str(note_id))
                )
        finally:
            conn.close()

    def search_semantic(self, query_embedding: List[float], top_k: int = 5) -> List[str]:
        """Search for top_k most similar notes."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        return [id for id in results['ids'][0]]

    def get_graph_neighbors(self, note_id: UUID, depth: int = 1) -> List[UUID]:
        """
        Perform a simple graph walk to find neighbors.
        In a real implementation, this would be recursive.
        """
        neighbors = []
        conn = sqlite3.connect(self.db_path, timeout=30)
        try:
            with conn:
                cursor = conn.cursor()
                # Find all edges connected to this note
                cursor.execute("""
                    SELECT source_id, target_id FROM edges
                    WHERE source_id = ? OR target_id = ?
                """, (str(note_id), str(note_id)))
                edges = cursor.fetchall()
                
                for source, target in edges:
                    # Add the other end of the edge
                    other = target if source == str(note_id) else source
                    if other and other != str(note_id):
                        # Convert string ID back to UUID
                        neighbors.append(UUID(other))
        finally:
            conn.close()
        
        return list(set(neighbors))
