import os
import re
from typing import List, Dict, Any
from src.models.models import Metadata

class MetadataExtractor:
    """
    Extracts structured metadata from the content of a file or note.
    """
    
    def __init__(self):
        pass

    def extract_from_content(self, content: str, file_path: str) -> Metadata:
        """
        Analyzes content to extract tags, title, and other metadata.
        """
        # Basic title: use filename or first non-empty line
        title = os.path.basename(file_path)
        
        # Simple tag extraction: look for #tags
        tags = []
        tag_matches = re.findall(r'#(\w+)', content)
        tags.extend([tag.lower() for tag in tag_matches])
        
        # Remove the # from the tag if it was captured
        # (Regex above captures only the word part)
        
        # Deduplicate
        tags = list(set(tags))

        # Content summary: first 200 characters
        content_summary = content[:200].strip() + "..." if len(content) > 200 else content.strip()

        return Metadata(
            title=title,
            tags=tags,
            source=file_path,
            content_summary=content_summary
        )
