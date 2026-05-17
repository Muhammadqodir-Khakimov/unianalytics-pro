"""Granular permission management.

Hozirgi 4 rol o'rniga aniq permissionlar:
- student.read, student.create, student.update, student.delete
- grade.create, grade.delete, grade.export
- report.create, report.export
- admin.users, admin.audit, admin.tenants
"""
from typing import Iterable

from sqlalchemy.orm import Session

from app.models.oltp.tenant import Permission, RolePermission
from app.models.oltp.user import UserRole


PERMISSIONS = [
    # Student CRUD
    ("student.read", "Talabalarni ko'rish", "student"),
    ("student.create", "Talaba yaratish", "student"),
    ("student.update", "Talaba ma'lumotini o'zgartirish", "student"),
    ("student.delete", "Talabani o'chirish", "student"),
    ("student.export", "Talabalar ro'yxatini eksport qilish", "student"),

    # Teacher
    ("teacher.read", "O'qituvchilarni ko'rish", "teacher"),
    ("teacher.create", "O'qituvchi yaratish", "teacher"),
    ("teacher.update", "O'qituvchi ma'lumotini o'zgartirish", "teacher"),
    ("teacher.delete", "O'qituvchini o'chirish", "teacher"),

    # Subject
    ("subject.read", "Fanlarni ko'rish", "subject"),
    ("subject.create", "Fan yaratish", "subject"),
    ("subject.update", "Fan ma'lumotini o'zgartirish", "subject"),
    ("subject.delete", "Fanni o'chirish", "subject"),

    # Grade
    ("grade.read", "Baholarni ko'rish", "grade"),
    ("grade.create", "Baho qo'shish", "grade"),
    ("grade.update", "Bahoni o'zgartirish", "grade"),
    ("grade.delete", "Bahoni o'chirish", "grade"),
    ("grade.import", "Baholarni CSV dan yuklash", "grade"),

    # OLAP
    ("olap.query", "OLAP query bajarish", "olap"),
    ("olap.export", "OLAP natijalarini eksport qilish", "olap"),

    # Analytics
    ("analytics.read", "Analitika ko'rish", "analytics"),
    ("analytics.atrisk", "Xavf zonasi ko'rish", "analytics"),
    ("analytics.predictions", "AI prognoz ko'rish", "analytics"),

    # Reports
    ("report.read", "Hisobotlarni ko'rish", "report"),
    ("report.generate", "Hisobot yaratish", "report"),

    # HEMIS
    ("announcement.create", "E'lon e'lon qilish", "hemis"),
    ("payment.read", "To'lovlarni ko'rish", "hemis"),
    ("payment.manage", "To'lov boshqaruvi", "hemis"),
    ("library.manage", "Kutubxonani boshqarish", "hemis"),
    ("dormitory.assign", "Yotoqxonaga biriktirish", "hemis"),
    ("thesis.manage", "Bitiruv ishlarini boshqarish", "hemis"),

    # Admin
    ("admin.users", "Foydalanuvchilar boshqaruvi", "admin"),
    ("admin.audit", "Audit log ko'rish", "admin"),
    ("admin.tenants", "Tashkilotlar boshqaruvi", "admin"),
    ("admin.permissions", "Ruxsatlarni boshqarish", "admin"),
    ("admin.webhooks", "Webhook lar boshqaruvi", "admin"),
    ("admin.system", "Tizim sozlamalari", "admin"),
]


# Default role mappings
DEFAULT_ROLE_PERMISSIONS = {
    UserRole.STUDENT.value: {
        "student.read",  # o'zini ko'ra oladi
        "subject.read",
        "grade.read",
        "report.read",
    },
    UserRole.TEACHER.value: {
        "student.read", "teacher.read", "subject.read",
        "grade.read", "grade.create", "grade.update", "grade.import",
        "report.read", "report.generate",
        "olap.query", "analytics.read",
    },
    UserRole.DEKAN.value: {
        "student.read", "student.create", "student.update", "student.export",
        "teacher.read", "teacher.create", "teacher.update",
        "subject.read", "subject.create", "subject.update",
        "grade.read", "grade.create", "grade.update", "grade.delete", "grade.import",
        "report.read", "report.generate", "olap.query", "olap.export",
        "analytics.read", "analytics.atrisk", "analytics.predictions",
        "announcement.create", "payment.read", "thesis.manage", "dormitory.assign",
    },
    UserRole.ADMIN.value: {p[0] for p in PERMISSIONS},  # hammasi
}


def seed_permissions(db: Session) -> int:
    """Boshlang'ich permissions va role-permissions ni yaratish."""
    count = 0
    for code, name, category in PERMISSIONS:
        existing = db.query(Permission).filter(Permission.code == code).first()
        if not existing:
            db.add(Permission(code=code, name=name, category=category))
            count += 1
    db.commit()

    # Permission ID lar
    perm_map = {p.code: p.id for p in db.query(Permission).all()}

    # Role-permissions
    for role, perms in DEFAULT_ROLE_PERMISSIONS.items():
        for perm_code in perms:
            pid = perm_map.get(perm_code)
            if not pid:
                continue
            existing = (
                db.query(RolePermission)
                .filter(RolePermission.role == role, RolePermission.permission_id == pid)
                .first()
            )
            if not existing:
                db.add(RolePermission(role=role, permission_id=pid, granted=True))
    db.commit()
    return count


def check_permission(db: Session, role: str, permission_code: str) -> bool:
    """Rol uchun ushbu permission bormi tekshirish."""
    perm = db.query(Permission).filter(Permission.code == permission_code).first()
    if not perm:
        return False
    rp = (
        db.query(RolePermission)
        .filter(RolePermission.role == role, RolePermission.permission_id == perm.id)
        .first()
    )
    return rp is not None and rp.granted


def get_role_permissions(db: Session, role: str) -> list[str]:
    """Rol uchun barcha permissionlar ro'yxati."""
    perms = (
        db.query(Permission, RolePermission)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .filter(RolePermission.role == role, RolePermission.granted == True)  # noqa: E712
        .all()
    )
    return [p[0].code for p in perms]


def get_all_permissions(db: Session) -> list[dict]:
    """Barcha permissions ro'yxati."""
    return [
        {"id": p.id, "code": p.code, "name": p.name, "category": p.category}
        for p in db.query(Permission).order_by(Permission.category, Permission.code).all()
    ]
