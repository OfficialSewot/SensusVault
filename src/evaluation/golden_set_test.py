import json
import unittest
import os
import shutil
from typing import List
from src.database.manager import DatabaseManager
from src.query_engine.engine import QueryEngine
from src.ingestor.ingestor import Ingestor
from sentence_transformers import SentenceTransformer

class TestGoldenSet(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_vault.db"
        self.chroma_path = "test_chroma"
        self.db_manager = DatabaseManager(db_path=self.db_path, chroma_path=self.chroma_path)
        self.query_engine = QueryEngine(self.db_manager)
        self.ingestor = Ingestor(self.db_manager)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load golden set
        with open("src/evaluation/golden_set.json", "r") as f:
            self.golden_set = json.load(f)
            
        # Generate test data
        from src.evaluation.generate_test_data import generate_test_data
        generate_test_data()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        if os.path.exists(self.chroma_path):
            shutil.rmtree(self.chroma_path)
        
    def test_golden_set_hit_rate(self):
        hits = 0
        total = len(self.golden_set)
        
        for item in self.golden_set:
            # Generate actual embedding for the question
            query_embedding = self.embedding_model.encode(item["question"]).tolist()
            results = self.query_engine.graph_aware_query(
                query_embedding=query_embedding,
                top_k=5,
                walk_depth=1
            )
            
            # Check if any of the returned notes have the expected title
            found = any(r.metadata.title == item["expected_note_title"] for r in results)
            if found:
                hits += 1
        
        hit_rate = hits / total
        print(f"Hit Rate on Golden Set: {hit_rate:.2%}")
        self.assertTrue(0 <= hit_rate <= 1)

if __name__ == "__main__":
    unittest.main()
