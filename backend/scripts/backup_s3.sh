#!/bin/sh
# Database backup → S3 (AWS S3 yoki MinIO)
# Cron: 0 3 * * *  /app/scripts/backup_s3.sh

set -e

DATE=$(date +%F-%H%M)
BACKUP_DIR="/tmp/backups"
mkdir -p "$BACKUP_DIR"

# PostgreSQL backup
PGPASSWORD="$OLTP_DB_PASSWORD" pg_dump \
  -h "$OLTP_DB_HOST" -U "$OLTP_DB_USER" -d "$OLTP_DB_NAME" \
  --format=custom --compress=9 \
  > "$BACKUP_DIR/oltp-$DATE.dump"

# Upload to S3
aws s3 cp "$BACKUP_DIR/oltp-$DATE.dump" \
  "s3://${S3_BACKUP_BUCKET}/oltp/oltp-$DATE.dump" \
  --storage-class STANDARD_IA

# Cleanup local
rm "$BACKUP_DIR/oltp-$DATE.dump"

# Delete old backups (>30 days)
aws s3 ls "s3://${S3_BACKUP_BUCKET}/oltp/" | \
  awk '$1 < "'$(date -d '30 days ago' +%F)'" {print $4}' | \
  xargs -I {} aws s3 rm "s3://${S3_BACKUP_BUCKET}/oltp/{}"

echo "Backup completed: oltp-$DATE.dump"
