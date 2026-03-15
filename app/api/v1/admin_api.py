from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies.auth_dependencies import get_current_user
from app.api.dependencies.dependencies import get_admin_service
from app.models.admin import AdminRead, AdminCreate, AdminUpdate
from app.services.admin_service import AdminService

router = APIRouter()


@router.post("", response_model=AdminRead)
def create_admin(admin: AdminCreate, service: AdminService = Depends(get_admin_service)):
    return service.create_admin(email=admin.email, password=admin.password, full_name=admin.full_name)


@router.get("", response_model=List[AdminRead])
def get_admins(service: AdminService = Depends(get_admin_service), current_user=Depends(get_current_user)):
    return service.get_admins()


@router.get("/{admin_id", response_model=AdminRead)
def get_admin(admin_id: int, service: AdminService = Depends(get_admin_service),
              current_user=Depends(get_current_user)):
    return service.get_admin(admin_id)


@router.delete("/{admin_id}")
def delete_admin(admin_id: int, service: AdminService = Depends(get_admin_service),
                 current_user=Depends(get_current_user)):
    success = service.delete_admin(admin_id)
    if not success:
        raise HTTPException(status_code=404, detail="Admin not found")
    return {"success": True}


@router.patch("/{admin_id}", response_model=AdminRead)
def update_admin(admin_id: int, admin: AdminUpdate, service: AdminService = Depends(get_admin_service),
                 current_user=Depends(get_current_user)):
    return service.update_message(admin_id=admin_id, email=admin.email, full_name=admin.full_name)
