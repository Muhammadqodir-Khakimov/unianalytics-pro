"""Bir martalik migrator: parent_link_requests.json + digest_settings.json -> OLTP.

Ishlatish (alembic upgrade head dan keyin):
    py -m scripts.migrate_parent_links_json_to_db [--dry-run]

Eski JSON fayllar:
    parent_link_requests.json   →  parent_links jadval
    digest_settings.json        →  user_preferences jadval

Migratsiya idempotent — qayta ishlatish xatosiz o'tadi.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from loguru import logger

from app.database import OLTPSession
from app.models.oltp.parent_link import (
    ParentLink,
    ParentLinkStatus,
    UserPreferences,
)
from app.models.oltp.student import Student
from app.models.oltp.user import User

PARENT_FILE = Path("parent_link_requests.json")
DIGEST_FILE = Path("digest_settings.json")


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        logger.error("Faylni o'qib bo'lmadi {}: {}", path, e)
        return {}


def migrate_parent_links(dry: bool) -> tuple[int, int]:
    data = _load(PARENT_FILE)
    if not data:
        return 0, 0

    created = skipped = 0
    with OLTPSession() as db:
        for req_id, rec in data.items():
            parent_user_id = rec.get("parent_user_id")
            hemis_id = rec.get("student_hemis_id")
            if not (parent_user_id and hemis_id):
                logger.warning("Yaroqsiz yozuv {}", req_id)
                skipped += 1
                continue

            student = (
                db.query(Student).filter(Student.student_id == hemis_id).first()
            )
            if not student:
                logger.warning("Talaba topilmadi: {}", hemis_id)
                skipped += 1
                continue

            if not db.query(User).filter(User.id == parent_user_id).first():
                logger.warning("Ota-ona user_id {} topilmadi", parent_user_id)
                skipped += 1
                continue

            exists = (
                db.query(ParentLink)
                .filter(
                    ParentLink.parent_user_id == parent_user_id,
                    ParentLink.student_id == student.id,
                )
                .first()
            )
            if exists:
                skipped += 1
                continue

            link = ParentLink(
                parent_user_id=parent_user_id,
                student_id=student.id,
                status=ParentLinkStatus(rec.get("status", "pending")),
                requested_at=_parse_dt(rec.get("created_at")) or datetime.utcnow(),
                decided_at=_parse_dt(rec.get("approved_at")),
            )
            db.add(link)
            created += 1

        if dry:
            db.rollback()
            logger.info("[DRY-RUN] parent_links: {} qo'shilardi, {} o'tkazib yuborildi",
                        created, skipped)
        else:
            db.commit()
            logger.info("parent_links: {} yangi yozuv, {} o'tkazib yuborildi",
                        created, skipped)
    return created, skipped


def migrate_digest(dry: bool) -> tuple[int, int]:
    data = _load(DIGEST_FILE)
    if not data:
        return 0, 0

    created = updated = 0
    with OLTPSession() as db:
        for user_id_str, enabled in data.items():
            try:
                user_id = int(user_id_str)
            except (TypeError, ValueError):
                continue
            if not db.query(User).filter(User.id == user_id).first():
                continue

            prefs = (
                db.query(UserPreferences)
                .filter(UserPreferences.user_id == user_id)
                .first()
            )
            if prefs:
                prefs.weekly_digest_enabled = bool(enabled)
                updated += 1
            else:
                db.add(UserPreferences(
                    user_id=user_id,
                    weekly_digest_enabled=bool(enabled),
                ))
                created += 1

        if dry:
            db.rollback()
            logger.info("[DRY-RUN] user_preferences: {} qo'shilardi, {} yangilanardi",
                        created, updated)
        else:
            db.commit()
            logger.info("user_preferences: {} yangi, {} yangilangan", created, updated)
    return created, updated


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Hech narsani saqlamaslik")
    args = parser.parse_args()

    logger.info("JSON -> OLTP migratsiya boshlandi (dry-run={})", args.dry_run)
    p_created, p_skipped = migrate_parent_links(args.dry_run)
    d_created, d_updated = migrate_digest(args.dry_run)

    logger.info(
        "Yakuniy: parent_links={}/{}, user_preferences={}/{}",
        p_created, p_skipped, d_created, d_updated,
    )

    if not args.dry_run and (p_created or d_created or d_updated):
        for path in (PARENT_FILE, DIGEST_FILE):
            if path.exists():
                backup = path.with_suffix(".json.migrated")
                path.rename(backup)
                logger.info("Eski fayl saqlandi: {}", backup)
    return 0


if __name__ == "__main__":
    sys.exit(main())
