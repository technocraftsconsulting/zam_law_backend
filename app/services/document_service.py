import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import Document
from app.db.schema import DocType, IngestionStatus, EventType
from app.services.admin_service import AdminService
from app.services.audit_log_service import AuditLogService

UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(exist_ok=True)


class DocumentService:
    def __init__(self, session: Session):
        self._db = session

    def upload_document(
            self,
            is_good_law: bool,
            jurisdiction: str,
            uploaded_document: UploadFile,
            current_user: int,
            admin_service: AdminService,
            audit_log_service: AuditLogService,
            decided_date: Optional[datetime] = None,
            citation: Optional[str] = None,
    ):
        if uploaded_document.filename == "":
            raise HTTPException(status_code=400, detail="No file selected")

        file_path = UPLOAD_DIR / uploaded_document.filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(uploaded_document.file, buffer)

        admin = admin_service.get_admin(current_user)

        document = Document(
            uploaded_by=admin.id,
            title=uploaded_document.filename,
            doc_type=DocType.OTHER.name,
            jurisdiction=jurisdiction,
            citation=citation,
            decided_date=decided_date,
            is_good_law=is_good_law,
            storage_path=str(file_path),
            ingestion_status=IngestionStatus.PENDING,
        )

        self._db.add(document)
        self._db.commit()
        self._db.refresh(document)

        audit_log_service.create_audit_log(
            event_type=EventType.DOCUMENT_UPLOADED.name,
            current_user=admin.id,
            entity_id=document.id,
            payload=list(str(document)),
            admin_service=admin_service
        )
        return document
