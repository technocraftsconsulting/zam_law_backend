from datetime import datetime

from pydantic import BaseModel


class DocumentCreate(BaseModel):
    uploaded_by: int
    title: str
    doc_type: str
    jurisdiction: str
    citation: str
    decided_date: datetime
    is_good_law: bool
    storage_path: str
    ingestion_status: str
    ingested_at: datetime


class DocumentRead(BaseModel):
    id: int
    uploaded_by: int
    title: str
    doc_type: str
    jurisdiction: str
    citation: str
    decided_date: datetime
    is_good_law: bool
    storage_path: str
    ingestion_status: str
    ingested_at: datetime
