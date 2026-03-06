from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.models.citation import CitationRead
from app.models.message import MessageRead
from app.models.retrieved_chunk import RetrievedChunkRead


class RagQueryCreate(BaseModel):
    session_id: int
    message_id: int
    raw_query: str
    detected_jurisdiction: str
    retrieval_ms: int
    generation_ms: int
    grounding_score: int
    hallucination_flags: int
    retrieved_chunks: List[RetrievedChunkRead]
    citations: List[CitationRead]


class RagQueryRead(BaseModel):
    id: int
    session_id: int
    message_id: int
    raw_query: str
    detected_jurisdiction: str
    retrieval_ms: int
    generation_ms: int
    grounding_score: int
    hallucination_flags: int
    created_at: datetime
    messages: List[MessageRead]
