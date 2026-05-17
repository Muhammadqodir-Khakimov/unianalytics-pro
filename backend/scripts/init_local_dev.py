"""Local dev uchun: jadvallarni yarat, seed va ETL bir buyruq bilan.

Ishga tushirish (backend papkasidan):
    py scripts/init_local_dev.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from loguru import logger

from app.database import OLAPBase, OLTPBase, olap_engine, oltp_engine
from app import models  # noqa: F401 -- modellarni yuklash


def main():
    logger.info("OLTP jadvallarni yaratish...")
    OLTPBase.metadata.drop_all(bind=oltp_engine)
    OLTPBase.metadata.create_all(bind=oltp_engine)

    logger.info("OLAP jadvallarni yaratish...")
    OLAPBase.metadata.drop_all(bind=olap_engine)
    OLAPBase.metadata.create_all(bind=olap_engine)

    logger.info("Seed data yuklash (bu bir necha daqiqa olishi mumkin)...")
    from scripts.seed_data import main as seed_main
    # Local dev uchun kichikroq hajm
    seed_main(reset=False, students=500, teachers=50, grades=5000)

    logger.info("ETL ishga tushirish (OLTP -> OLAP)...")
    from app.services.etl_service import run_full_etl
    stats = run_full_etl()
    logger.success("Tayyor! ETL stats: {}", stats)


if __name__ == "__main__":
    main()
