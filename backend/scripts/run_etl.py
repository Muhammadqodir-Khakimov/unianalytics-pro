"""ETL ni qo'lda ishga tushirish (Celery ishlatmay).

Ishga tushirish:
    docker-compose exec backend python scripts/run_etl.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from loguru import logger

from app.database import OLAPBase, olap_engine
from app.services.etl_service import run_full_etl


def main():
    logger.info("OLAP jadvallarni yaratish...")
    OLAPBase.metadata.create_all(bind=olap_engine)
    logger.info("ETL boshlanmoqda...")
    stats = run_full_etl()
    logger.success("ETL tugadi: {}", stats)


if __name__ == "__main__":
    main()
