from typing import List, Dict, Any
from gliner import GLiNER
import torch

class EntityExtractor:
    def __init__(self, model_name: str = "urchade/gliner_multi-v2.1"):
        """
        Initializes the GLiNER model for fast, lightweight entity extraction.
        """
        # Use GPU if available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = GLiNER.from_pretrained(model_name).eval()
        self.model.to(device)

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts entities from text using GLiNER.
        """
        # Define labels of interest for a knowledge engine
        labels = ["person", "organization", "location", "project", "technology", "concept"]
        
        entities = self.model.predict_entities(text, labels, threshold=0.5)
        
        # Format output: [{"text": "...", "type": "...", "score": ...}]
        results = []
        for entity in entities:
            if entity:
                print(f"DEBUG: entity keys: {entity.keys()}")
            results.append({
                "text": entity["text"],
                "type": entity.get("type") or entity.get("label") or "unknown",
                "score": entity["score"]
            })
        return results
