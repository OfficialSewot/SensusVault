from fastapi import FastAPI, HTTPException
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
        dummy_embedding = [0.1] * 1536 
        
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
    db_manager.update_action_status(UUID(action_id), "approved")
    return {"message": f"Action {action_id} approved"}

@app.post("/actions/{action_id}/reject")
def reject_action(action_id: str):
    """
    Rejects a pending action.
    """
    db_manager.update_action_status(UUID(action_id), "rejected")
    return {"message": f"Action {action_id} rejected"}

@app.post("/actions/{action_id}/execute")
def execute_action(action_id: str):
    """
    Executes an approved action.
    """
    db_manager.execute_action(UUID(action_id))
    return {"message": f"Action {action_id} executed"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
