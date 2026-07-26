from typing import List, Dict, Any
from uuid import UUID
from src.database.manager import DatabaseManager
from src.models.models import Note, Metadata, Action
import json

class AgentTools:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def create_note(self, content: str, title: str, source: str, tags: List[str]) -> str:
        """
        Proposes creating a new note in the vault.
        """
        action = Action(
            type="create_note",
            payload={
                "content": content,
                "title": title,
                "source": source,
                "tags": tags
            }
        )
        self.db_manager.add_action(action)
        return "Action proposed: create_note"

    def delete_note(self, note_id: str) -> bool:
        """
        Deletes a note from the vault.
        This action will be added to the Action Queue.
        """
        # The agent doesn't delete directly; it proposes an action
        action = Action(
            type="delete_note",
            payload={"note_id": note_id}
        )
        self.db_manager.add_action(action)
        return True

    def update_metadata(self, note_id: str, new_metadata_dict: Dict[str, Any]) -> bool:
        """
        Updates the metadata of an existing note.
        """
        # Propose an action
        action = Action(
            type="update_metadata",
            payload={"note_id": note_id, "metadata": new_metadata_dict}
        )
        self.db_manager.add_action(action)
        return True

    def generate_graph_link(self, source_note_id: str, target_note_id: str, relation: str) -> bool:
        """
        Creates a link between two notes in the knowledge graph.
        """
        action = Action(
            type="generate_graph_link",
            payload={
                "source_id": source_note_id,
                "target_id": target_note_id,
                "relation": relation
            }
        )
        self.db_manager.add_action(action)
        return True

    def suggest_links(self, note_id: str) -> List[Dict[str, Any]]:
        """
        Suggests links based on graph proximity.
        """
        # This is a tool for the agent to discover potential connections
        # and then it can choose to call generate_graph_link.
        neighbors = self.db_manager.get_graph_neighbors(UUID(note_id))
        suggestions = []
        for neighbor_id in neighbors:
            suggestions.append({
                "note_id": str(neighbor_id),
                "reason": f"Graph neighbor (proximity)"
            })
        return suggestions

    def summarize_note(self, note_id: str) -> str:
        """
        Summarizes a note's content.
        This action will be added to the Action Queue.
        """
        note = self.db_manager.get_note(UUID(note_id))
        if not note:
            return "Note not found."
        
        # In a real scenario, this would call an LLM for summarization.
        # For now, we propose an action to update the summary.
        summary = f"Summary of: {note.content[:100]}..."
        
        action = Action(
            type="update_metadata",
            payload={
                "note_id": note_id,
                "metadata": {
                    "content_summary": summary
                }
            }
        )
        self.db_manager.add_action(action)
        return "Action proposed: summarize_note"
