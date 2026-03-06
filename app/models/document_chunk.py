from typing import List

from pydantic import BaseModel

from app.models.document import DocumentRead


class DocumentChunkCreate(BaseModel):
    document_id: int
    vector_id: int
    chunk_index: int
    text_preview: str
    section_path: List[str]
    is_holding: bool
    precedential: str
    prev_chunk_id: int
    next_chunk_id: int
    token_count: int
    document: DocumentRead


class DocumentChunkRead(BaseModel):
    id: int
    document_id: int
    vector_id: int
    chunk_index: int
    text_preview: str
    section_path: List[str]
    is_holding: bool
    precedential: str
    prev_chunk_id: int
    next_chunk_id: int
    token_count: int
