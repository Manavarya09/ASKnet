from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class QueryRequest(BaseModel):
    user_id: str
    query_text: str
    constraints: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    task_id: str
    status: str
    timestamp: datetime


class TaskStatus(BaseModel):
    task_id: str
    status: str
    query_text: str
    domain: Optional[str] = None
    assignments: List[Dict[str, Any]] = []
    final_answer: Optional[str] = None
    debate_history: Optional[List[Dict[str, Any]]] = None
    created_at: datetime
    updated_at: datetime


class FeedbackRequest(BaseModel):
    task_id: str
    rating: int  # 1-5
    comments: Optional[str] = None


class MessagePayload(BaseModel):
    sender: str
    receiver: str
    message: str
    confidence: float
    timestamp: Optional[str] = None
    context_id: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
