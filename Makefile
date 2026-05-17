.PHONY: help up down build logs test seed etl migrate clean prod

help:
	@echo "Asosiy buyruqlar:"
	@echo "  make up        - Servislarni ishga tushirish (dev)"
	@echo "  make down      - Servislarni to'xtatish"
	@echo "  make build     - Image larni qayta qurish"
	@echo "  make seed      - Test ma'lumotlarini yuklash"
	@echo "  make etl       - ETL ishga tushirish (OLTP -> OLAP)"
	@echo "  make test      - Backend testlarni ishga tushirish"
	@echo "  make logs      - Loglarni kuzatish"
	@echo "  make migrate   - Alembic migration"
	@echo "  make prod      - Production ishga tushirish"
	@echo "  make clean     - Hammasini tozalash (volume larni ham)"

up:
	docker-compose up -d
	@echo "Tizim ishga tushdi:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend:  http://localhost:8000/docs"

down:
	docker-compose down

build:
	docker-compose build

logs:
	docker-compose logs -f

seed:
	docker-compose exec backend python scripts/seed_data.py

etl:
	docker-compose exec backend python scripts/run_etl.py

test:
	docker-compose exec backend pytest

migrate: migrate-oltp migrate-olap

migrate-oltp:
	docker-compose exec backend alembic -x target=oltp upgrade oltp@head

migrate-olap:
	docker-compose exec backend alembic -x target=olap upgrade olap@head

migrate-status:
	docker-compose exec backend alembic -x target=oltp current
	docker-compose exec backend alembic -x target=olap current

prod:
	docker-compose -f docker-compose.prod.yml up -d

clean:
	docker-compose down -v
	docker-compose -f docker-compose.prod.yml down -v
