"""Granular permission boshqaruv endpointlari."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_admin
from app.database import get_oltp_db
from app.models.oltp.tenant import Permission, RolePermission
from app.models.oltp.user import User, UserRole
from app.services import permission_service

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.get("")
def list_permissions(
    db: Session = Depends(get_oltp_db),
    user: User = Depends(get_current_user),
):
    """Joriy user ning permissionlari."""
    return {
        "role": user.role.value,
        "permissions": permission_service.get_role_permissions(db, user.role.value),
    }


@router.get("/all", dependencies=[Depends(require_admin)])
def all_permissions(db: Session = Depends(get_oltp_db)):
    return permission_service.get_all_permissions(db)


@router.get("/roles", dependencies=[Depends(require_admin)])
def role_permissions(db: Session = Depends(get_oltp_db)):
    """Har rol uchun permissionlar ro'yxati."""
    return {
        role.value: permission_service.get_role_permissions(db, role.value)
        for role in UserRole
    }


class PermissionToggle(BaseModel):
    role: str
    permission_code: str
    granted: bool


@router.post("/toggle", dependencies=[Depends(require_admin)])
def toggle_permission(payload: PermissionToggle, db: Session = Depends(get_oltp_db)):
    perm = db.query(Permission).filter(Permission.code == payload.permission_code).first()
    if not perm:
        raise HTTPException(404, "Permission topilmadi")
    rp = (
        db.query(RolePermission)
        .filter(RolePermission.role == payload.role, RolePermission.permission_id == perm.id)
        .first()
    )
    if rp:
        rp.granted = payload.granted
    else:
        rp = RolePermission(role=payload.role, permission_id=perm.id, granted=payload.granted)
        db.add(rp)
    db.commit()
    return {"success": True}


@router.post("/seed", dependencies=[Depends(require_admin)])
def seed_default_permissions(db: Session = Depends(get_oltp_db)):
    """Default permissions va role-mapping ni boshlang'ich holatga keltirish."""
    count = permission_service.seed_permissions(db)
    return {"new_permissions": count, "success": True}
