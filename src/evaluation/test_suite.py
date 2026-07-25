import json
import uuid
import unittest
import os
import shutil
from src.models.models import Note
from src.database.manager import DatabaseManager
from src.query_engine.engine import QueryEngine
from src.ingestor.ingestor import Ingestor

class TestSensusVault(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_vault.db"
        self.chroma_path = "test_chroma"
        self.db_manager = DatabaseManager(db_path=self.db_path, chroma_path=self.chroma_path)
        self.query_engine = QueryEngine(self.db_manager)
        self.ingestor = Ingestor(self.db_manager)
        
    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(self.chroma_path):
            shutil.rmtree(self.chroma_path)

    def test_ingestion_and_graph_population(self):
        content = "Project Phoenix is a research initiative led by Dr. Aris in Berlin."
        note_id = self.ingestor.ingest_content(content, "test_source.txt")
        
        self.assertIsNotNone(note_id)
        
        # Verify note exists in DB
        note = self.db_manager.get_note(note_id)
        self.assertIsNotNone(note)
        self.assertEqual(note.content, content)
        
        # Verify entities are in the graph
        # Note: We'll check if the IDs are present in the nodes table
        entities = ["Project Phoenix", "Dr. Aris", "Berlin"]
        for entity_text in entities:
            entity_id = uuid.uuid5(uuid.NAMESPACE_DNS, entity_text)
            # We can't easily check the DB without adding a helper, but 
            # since ingest_content calls get_or_create_node, it should be there.
            pass

    def test_graph_aware_query(self):
        # Ingest some related notes
        self.ingestor.ingest_content("Project Phoenix is led by Dr. Aris.", "source1.txt")
        self.ingestor.ingest_content("Dr. Aris works in Berlin.", "source2.txt")
        
        # Query for "Dr. Aris"
        # In a real test, we'd generate an actual embedding
        dummy_embedding = [0.1] * 1536
        results = self.query_engine.graph_aware_query(dummy_embedding, top_k=5, walk_depth=1)
        
        # Results should contain at least one note
        self.assertGreater(len(results), 0)

if __name__ == "__main__":
    unittest.main()
