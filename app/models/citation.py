from datetime import datetime

from pydantic import BaseModel

from app.models.document_chunk import DocumentChunkRead


class CitationCreate(BaseModel):
    query_id: int
    chunk_id: int
    raw_citation_text: str
    verified: bool
    verification_method: str


class CitationRead(BaseModel):
    id: int
    query_id: int
    chunk_id: int
    raw_citation_text: str
    verified: bool
    verification_method: str
    created_at: datetime
    document_chunk: DocumentChunkRead
