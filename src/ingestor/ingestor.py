import os
import uuid
from typing import Optional
import os
import uuid
from typing import Optional
from src.models.models import Note
from src.pre_processor.processor import PreProcessor
from src.pre_processor.metadata_extractor import MetadataExtractor
from src.database.manager import DatabaseManager

class Ingestor:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.pre_processor = PreProcessor()
        self.metadata_extractor = MetadataExtractor()

    def ingest_file(self, file_path: str) -> Optional[uuid.UUID]:
        """
        Ingests a file into the vault with atomic sync.
        """
        print(f"Ingesting: {file_path}")
        
        # 1. Extract text
        text = self.pre_processor.process(file_path)
        if not text:
            print(f"Warning: No text extracted from {file_path}")
            return None

        # 2. Extract Metadata
        metadata = self.metadata_extractor.extract_from_content(text, file_path)

        # 3. Generate UUID
        note_id = uuid.uuid4()

        # 4. Create Note object
        # Note: Embeddings would be generated here by an embedding model
        note = Note(
            id=note_id,
            content=text,
            metadata=metadata,
            embedding=None # Placeholder for now
        )

        # 5. Atomic Sync (Delete-then-Insert)
        # In a production scenario, we would check if a note with the same source path
        # already exists, retrieve its UUID, and call self.db_manager.delete_note(old_id)
        
        self.db_manager.insert_note(note)
        print(f"Successfully ingested {file_path} with ID: {note_id}")
        
        return note_id
