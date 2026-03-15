from pathlib import Path

import magic
from fastapi import Depends, APIRouter, UploadFile, File, HTTPException
from starlette import status
from starlette.formparsers import MultiPartParser

from app.api.dependencies.auth_dependencies import get_current_user
from app.api.dependencies.dependencies import get_document_service, get_audit_log_service
from app.api.v1.admin_api import get_admin_service
from app.core.config import settings
from app.services.audit_log_service import AuditLogService
from app.services.document_service import DocumentService

router = APIRouter()

MultiPartParser.max_part_size = settings.max_upload_size * 1024 * 1024
acceptable_file_extensions = ['.csv', '.pdf', '.xlsx', '.docx', '.jpg', '.jpeg']
allowed_mime_types = ["image/jpeg", "application/pdf", "application/octet-stream", "text/csv", "application/msword",
                      "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]


@router.post("")
async def upload_document(file: UploadFile = File(), service: DocumentService = Depends(get_document_service),
                          current_user=Depends(get_current_user), admin_service=Depends(get_admin_service),
                          audit_log_service: AuditLogService = Depends(get_audit_log_service)):
    try:
        file_path = Path(file.filename)
        extension = file_path.suffix
        if extension not in acceptable_file_extensions:
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                                detail="File extension is not supported.")
        else:
            contents = await file.read()
            file.file.seek(0)

            mime_type = magic.from_buffer(contents, mime=True)
            if mime_type not in allowed_mime_types:
                raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported file type.")

            current_user_id = current_user.id
            service.upload_document(uploaded_document=file,
                                    is_good_law=True,
                                    jurisdiction="Lusaka",
                                    current_user=current_user_id,
                                    admin_service=admin_service, audit_log_service=audit_log_service)

    except Exception as e:
        print("The error is: ")
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An error occurred while processing the file.")
    return {"success": "File uploaded successfully."}
