import os
from typing import List
from sentence_transformers import SentenceTransformer

class EmbeddingManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self._initialized = True

    def encode(self, text: str) -> List[float]:
        """
        Encodes text into a list of floats.
        """
        return self.model.encode(text).tolist()
