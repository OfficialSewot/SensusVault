from typing import List, Optional
from uuid import UUID
from src.database.manager import DatabaseManager
from src.embeddings.manager import EmbeddingManager
from src.models.models import Note

class QueryEngine:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def graph_aware_query(self, query_embedding: List[float], top_k: int = 5, walk_depth: int = 1) -> List[Note]:
        """
        Performs a Graph-Aware RAG query:
        1. Semantic Search: Find the top-k most relevant notes.
        2. Graph Walk: For each note, find its neighbors in the knowledge graph.
        3. Aggregate: Return unique notes found in both steps.
        """
        # Step 1: Semantic Search
        semantic_ids = self.db_manager.search_semantic(query_embedding, top_k=top_k)
        print(f"DEBUG: Semantic Search returned IDs: {semantic_ids}")
        
        # Step 2: Graph Walk
        all_related_ids = set(semantic_ids)
        for note_id_str in semantic_ids:
            note_id = UUID(note_id_str)
            neighbors = self.db_manager.get_graph_neighbors(note_id, depth=walk_depth)
            print(f"DEBUG: Neighbors for {note_id_str}: {neighbors}")
            for neighbor_id in neighbors:
                all_related_ids.add(str(neighbor_id))
        
        print(f"DEBUG: All related IDs after graph walk: {all_related_ids}")
        
        # Step 3: Aggregate results
        results = []
        for note_id_str in all_related_ids:
            note_id = UUID(note_id_str)
            note = self.db_manager.get_note(note_id)
            if note:
                results.append(note)
        
        print(f"DEBUG: Final results count: {len(results)}")
        return results
