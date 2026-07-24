import sqlite3
import json
from uuid import UUID
from typing import List, Optional, Dict, Any
from src.models.models import Metadata, Note

class DatabaseManager:
    def __init__(self, db_path: str = "vault.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
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
            conn.commit()

    def delete_note(self, note_id: UUID):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Delete from notes
            cursor.execute("DELETE FROM notes WHERE id = ?", (str(note_id),))
            # Delete associated graph nodes (simplified: delete node if it matches ID)
            cursor.execute("DELETE FROM nodes WHERE id = ?", (str(note_id),))
            # Delete edges where this note is source or target
            cursor.execute("DELETE FROM edges WHERE source_id = ? OR target_id = ?", (str(note_id), str(note_id)))
            conn.commit()

    def insert_note(self, note: Note):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notes (id, content, metadata, embedding) VALUES (?, ?, ?, ?)",
                (str(note.id), note.content, note.metadata.json(), json.dumps(note.embedding) if note.embedding else None)
            )
            # Insert as a node
            cursor.execute(
                "INSERT INTO nodes (id, type, metadata) VALUES (?, ?, ?)",
                (str(note.id), "note", note.metadata.json())
            )
            conn.commit()

    def add_edge(self, source_id: UUID, target_id: UUID, relation: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO edges (source_id, target_id, relation_type) VALUES (?, ?, ?)",
                (str(source_id), str(target_id), relation)
            )
            conn.commit()

    def get_note(self, note_id: UUID) -> Optional[Note]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT content, metadata FROM notes WHERE id = ?", (str(note_id),))
            row = cursor.fetchone()
            if row:
                metadata = Metadata.parse_raw(row[1])
                return Note(id=note_id, content=row[0], metadata=metadata)
        return None
