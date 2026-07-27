from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class Metadata(BaseModel):
    title: str
    tags: List[str] = Field(default_factory=list)
    date_created: datetime = Field(default_factory=datetime.now)
    source: str
    content_summary: Optional[str] = None
    status: str = "raw"
    project_id: Optional[UUID] = None

class Note(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    content: str
    metadata: Metadata
    embedding: Optional[List[float]] = None

class Action(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: str
    payload: dict
    status: str = "pending"  # pending, approved, rejected
    created_at: datetime = Field(default_factory=datetime.now)
