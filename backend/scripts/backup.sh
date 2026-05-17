#!/bin/bash
# PostgreSQL backup script
# Cron orqali kunlik ishga tushirish: 0 3 * * * /app/scripts/backup.sh

set -e
DATE=$(date +%F-%H%M)
BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"

mkdir -p "$BACKUP_DIR"

echo "[$(date)] Backup boshlandi..."

# OLTP backup
PGPASSWORD="$OLTP_DB_PASSWORD" pg_dump \
    -h "$OLTP_DB_HOST" \
    -U "$OLTP_DB_USER" \
    -d "$OLTP_DB_NAME" \
    --format=custom \
    --compress=9 \
    > "$BACKUP_DIR/oltp-$DATE.dump"
echo "  OLTP: $(ls -lh $BACKUP_DIR/oltp-$DATE.dump | awk '{print $5}')"

# OLAP backup
PGPASSWORD="$OLAP_DB_PASSWORD" pg_dump \
    -h "$OLAP_DB_HOST" \
    -U "$OLAP_DB_USER" \
    -d "$OLAP_DB_NAME" \
    --format=custom \
    --compress=9 \
    > "$BACKUP_DIR/olap-$DATE.dump"
echo "  OLAP: $(ls -lh $BACKUP_DIR/olap-$DATE.dump | awk '{print $5}')"

# Eski backup larni o'chirish
find "$BACKUP_DIR" -name "*.dump" -mtime +$RETENTION_DAYS -delete
echo "  Eski backups (>${RETENTION_DAYS} kun) o'chirildi"

echo "[$(date)] Backup tugadi."
