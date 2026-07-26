from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SensusVault API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from pydantic import BaseModel
from typing import List, Optional
import uuid
import json

from src.database.manager import DatabaseManager
from src.query_engine.engine import QueryEngine
from src.models.models import Note

app = FastAPI(title="SensusVault API")

# Initialize components
db_manager = DatabaseManager()
query_engine = QueryEngine(db_manager)

class QueryRequest(BaseModel):
    query_text: str
    top_k: Optional[int] = 5
    walk_depth: Optional[int] = 1

class ActionResponse(BaseModel):
    id: str
    type: str
    payload: dict
    status: str
    created_at: str

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/query")
async def query(request: QueryRequest):
    """
    Endpoint for semantic search with graph-aware expansion.
    In a full implementation, query_text would be converted to an embedding 
    using an embedding model before calling query_engine.
    """
    try:
        # Placeholder: In production, replace with actual embedding generation
        # e.g., embedding = embedding_model.encode(request.query_text)
        dummy_embedding = [0.1] * 384
        
        results = query_engine.graph_aware_query(
            query_embedding=dummy_embedding,
            top_k=request.top_k,
            walk_depth=request.walk_depth
        )
        
        return {
            "query": request.query_text,
            "results": [
                {
                    "id": str(note.id),
                    "title": note.metadata.title,
                    "content_summary": note.metadata.content_summary,
                    "tags": note.metadata.tags
                }
                for note in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/actions", response_model=List[ActionResponse])
def list_actions():
    """
    Lists all pending actions from the queue.
    """
    actions = db_manager.get_pending_actions()
    return [
        ActionResponse(
            id=str(a.id),
            type=a.type,
            payload=a.payload,
            status=a.status,
            created_at=a.created_at.isoformat()
        ) for a in actions
    ]

@app.post("/actions/{action_id}/approve")
def approve_action(action_id: str):
    """
    Approves a pending action.
    """
    db_manager.update_action_status(action_id, "approved")
    return {"message": f"Action {action_id} approved"}

@app.post("/actions/{action_id}/reject")
def reject_action(action_id: str):
    """
    Rejects a pending action.
    """
    db_manager.update_action_status(action_id, "rejected")
    return {"message": f"Action {action_id} rejected"}

@app.post("/actions/{action_id}/execute")
def execute_action(action_id: str):
    """
    Executes an approved action.
    """
    db_manager.execute_action(action_id)
    return {"message": f"Action {action_id} executed"}

@app.post("/notes")
async def create_note(data: dict):
    """
    Endpoint to create a new note in the database.
    """
    try:
        from src.models.models import Note, Metadata
        note = Note(
            content=data["content"],
            metadata=Metadata(
                title=data["title"],
                source=data["source"],
                tags=data.get("tags", [])
            )
        )
        db_manager.insert_note(note)
        return {"message": "Note created successfully", "id": str(note.id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notes")
async def list_notes():
    """
    Endpoint to list all notes.
    """
    try:
        notes = db_manager.list_notes()
        return [
            {
                "id": str(note.id),
                "content": note.content,
                "metadata": note.metadata.model_dump()
            }
            for note in notes
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notes/{note_id}")
async def get_note(note_id: str):
    """
    Endpoint to retrieve a note by its ID.
    """
    try:
        from uuid import UUID
        note = db_manager.get_note(UUID(note_id))
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return {
            "id": str(note.id),
            "content": note.content,
            "metadata": note.metadata.model_dump()
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
