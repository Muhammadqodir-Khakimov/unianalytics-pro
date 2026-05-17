# Deploy yo'riqnomasi

## Local development

```bash
docker-compose up -d
```

Servislar:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Swagger: http://localhost:8000/docs

## Production deployment

### 1. Server tayyorlash
- Ubuntu 22.04 LTS / Debian 12
- 4 vCPU, 8 GB RAM minimum
- 50 GB disk
- Docker Engine 24+
- Docker Compose v2

### 2. SSL sertifikat
Let's Encrypt orqali:
```bash
sudo certbot certonly --standalone -d yourdomain.uz
cp /etc/letsencrypt/live/yourdomain.uz/*.pem ./nginx/ssl/
```

### 3. Environment
`.env` faylda barcha parollarni o'zgartiring:
- `SECRET_KEY` — kuchli random string
- DB parollar
- `APP_DEBUG=false`
- `APP_ENV=production`

### 4. Ishga tushirish
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 5. Migration va seed
```bash
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
docker-compose -f docker-compose.prod.yml exec backend python scripts/seed_data.py --production
```

## Backup

PostgreSQL dump kunlik:
```bash
docker exec olap-postgres-oltp pg_dump -U oltp_user student_oltp > backup-oltp-$(date +%F).sql
docker exec olap-postgres-olap pg_dump -U olap_user student_olap > backup-olap-$(date +%F).sql
```

## Monitoring

- Flower (Celery): http://localhost:5555
- Health check: http://localhost:8000/health
- Logs: `docker-compose logs -f <service>`

## Restart va yangilash

```bash
git pull
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```
