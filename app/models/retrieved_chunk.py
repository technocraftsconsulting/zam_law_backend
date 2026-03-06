from pydantic import BaseModel


class RetrievedChunkCreate(BaseModel):
    query_id: int
    chunk_id: int
    rank_position: int
    dense_score: float
    sparse_score: float
    rerank_score: float
    used_in_context: bool


class RetrievedChunkRead(BaseModel):
    id: int
    query_id: int
    chunk_id: int
    rank_position: int
    dense_score: float
    sparse_score: float
    rerank_score: float
    used_in_context: bool
