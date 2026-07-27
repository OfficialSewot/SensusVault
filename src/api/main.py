from fastapi import FastAPI, HTTPException, BackgroundTasks
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
import os

from src.database.manager import DatabaseManager
from src.query_engine.engine import QueryEngine
from src.embeddings.manager import EmbeddingManager
from src.models.models import Note
from src.pre_processor.note_processor import NoteProcessor

# Initialize components
db_manager = DatabaseManager()
query_engine = QueryEngine(db_manager)
embedding_manager = EmbeddingManager()
note_processor = NoteProcessor(db_manager)


@app.get("/debug/db")
def debug_db():
    return {
        "cwd": os.getcwd(),
        "db_path_relative": db_manager.db_path,
        "db_path_absolute": os.path.abspath(db_manager.db_path)
    }

class QueryRequest(BaseModel):
    query_text: str
    top_k: Optional[int] = 5
    walk_depth: Optional[int] = 1

class CaptureRequest(BaseModel):
    title: str
    content: str
    project_id: Optional[str] = None

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
    """
    try:
        embedding_manager = EmbeddingManager()
        query_embedding = embedding_manager.encode(request.query_text)
        
        results = query_engine.graph_aware_query(
            query_embedding=query_embedding,
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

@app.get("/graph")
async def get_graph():
    """
    Endpoint to retrieve all nodes and edges for the knowledge graph.
    """
    try:
        nodes = db_manager.get_all_nodes()
        edges = db_manager.get_all_edges()
        return {
            "nodes": nodes,
            "edges": edges
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/notes/capture")
async def capture_note(request: CaptureRequest, background_tasks: BackgroundTasks):
    """
    Endpoint for quick capture of raw notes.
    """
    try:
        from src.models.models import Note, Metadata
        from uuid import UUID
        
        # Parse project_id if provided
        p_id = None
        if request.project_id:
            try:
                p_id = UUID(request.project_id)
            except ValueError:
                pass

        note = Note(
            content=request.content,
            metadata=Metadata(
                title=request.title,
                source="manual",
                tags=[],
                status="raw",
                project_id=p_id
            )
        )
        db_manager.insert_note(note)
        
        # Trigger background processing
        background_tasks.add_task(process_note_background, str(note.id))
        
        return {"message": "Note captured successfully", "id": str(note.id)}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))

def process_note_background(note_id: str):
    """
    Background task to process a note immediately after capture.
    """
    try:
        note_processor.process_note(note_id)
    except Exception as e:
        print(f"Error in background processing: {e}")

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

@app.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    """
    Endpoint to delete a note from the database.
    """
    try:
        db_manager.delete_note(note_id)
        return {"message": "Note deleted successfully"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
