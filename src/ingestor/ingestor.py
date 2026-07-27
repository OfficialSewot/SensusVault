import os
import uuid
import json
from typing import Optional, List, Dict, Any
from src.models.models import Note
from src.pre_processor.processor import PreProcessor
from src.pre_processor.metadata_extractor import MetadataExtractor
from src.pre_processor.ner import EntityExtractor
from src.database.manager import DatabaseManager
from src.embeddings.manager import EmbeddingManager

class Ingestor:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.pre_processor = PreProcessor()
        self.metadata_extractor = MetadataExtractor()
        self.entity_extractor = EntityExtractor()
        self.embedding_manager = EmbeddingManager()

    def ingest_file(self, file_path: str) -> Optional[uuid.UUID]:
        """
        Ingests a file into the vault with atomic sync and graph population.
        """
        print(f"Ingesting: {file_path}")
        
        # 1. Extract text
        text = self.pre_processor.process(file_path)
        if not text:
            print(f"Warning: No text extracted from {file_path}")
            return None

        return self.ingest_content(text, file_path)

    def ingest_content(self, content: str, source: str) -> Optional[uuid.UUID]:
        """
        Ingests raw content into the vault with atomic sync and graph population.
        """
        print(f"Ingesting content from {source}")

        # 1. Extract Metadata
        metadata = self.metadata_extractor.extract_from_content(content, source)

        # 2. Extract Entities
        entities = self.entity_extractor.extract_entities(content)
        
        # 3. Generate UUID
        note_id = uuid.uuid4()

        # 4. Create Note object
        # Generate embedding for the content
        embedding = self.embedding_manager.encode(content)

        note = Note(
            id=note_id,
            content=content,
            metadata=metadata,
            embedding=embedding
        )

        # 5. Atomic Sync (Insert Note & Populate Graph)
        # Insert the main note (this also creates the 'note' node in SQLite)
        self.db_manager.insert_note(note)
        
        # Connect note to extracted entities in the graph
        for entity in entities:
            entity_text = entity["text"]
            # Use a deterministic UUID for the entity based on its text
            entity_id = uuid.uuid5(uuid.NAMESPACE_DNS, entity_text)
            
            # Upsert the entity node
            self.db_manager.get_or_create_node(entity_id, "entity", json.dumps({
                "text": entity_text,
                "type": entity["type"],
                "score": entity["score"]
            }))
            
            # Create the relation (edge)
            self.db_manager.add_edge(note_id, entity_id, "contains_entity")

        print(f"Successfully ingested content with ID: {note_id}")
        
        return note_id
