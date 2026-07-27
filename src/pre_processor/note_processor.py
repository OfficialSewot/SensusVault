from typing import List, Dict, Any
from uuid import UUID
from src.models.models import Note, Metadata
from src.database.manager import DatabaseManager
from src.pre_processor.metadata_extractor import MetadataExtractor
from src.pre_processor.ner import EntityExtractor

class NoteProcessor:
    """
    Handles the background processing of captured notes, including 
    entity extraction, summary generation, and tag assignment.
    """
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.metadata_extractor = MetadataExtractor()
        self.entity_extractor = EntityExtractor()

    def process_note(self, note_id: str) -> Note:
        """
        Processes a note by extracting entities and updating its metadata.
        """
        try:
            note_uuid = UUID(note_id)
            note = self.db_manager.get_note(note_uuid)
            if not note:
                return None

            # 1. Extract entities using GLiNER
            entities = self.entity_extractor.extract_entities(note.content)
            
            # Create tags from entities with a score threshold
            entity_tags = []
            for entity in entities:
                if entity["score"] > 0.5:
                    # Clean the text for tags (lowercase, remove special chars)
                    tag = entity["text"].lower().replace(" ", "_")
                    entity_tags.append(f"#{tag}")

            # 2. Generate content summary if not already present
            content_summary = note.metadata.content_summary
            if not content_summary:
                content_summary = note.content[:200].strip() + "..." if len(note.content) > 200 else note.content.strip()

            # 3. Update metadata
            # We combine existing tags, new entity tags, and mandatory status tags
            new_tags = list(set(note.metadata.tags + entity_tags + ["#status:processed", "#source:manual"]))
            
            new_metadata = Metadata(
                title=note.metadata.title,
                tags=new_tags,
                source=note.metadata.source,
                content_summary=content_summary,
                status="processed",
                project_id=note.metadata.project_id
            )

            # 4. Persist changes
            self.db_manager.update_note_metadata(note_uuid, new_metadata)
            
            # Update the local note object for consistency
            note.metadata = new_metadata
            return note
        except Exception as e:
            print(f"Error processing note {note_id}: {e}")
            return None
