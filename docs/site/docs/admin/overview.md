---
sidebar_position: 1
---

# Administrator qo'llanma

## Vazifalar

- Foydalanuvchilar va rollar
- Fakultet / kafedra / fan tarkibi
- HEMIS sinxronlashtirish
- ETL jobs nazorat
- Backup va monitoring

## Foydalanuvchi qo'shish

1. Boshqaruv → Foydalanuvchilar → "Qo'shish"
2. Email, parol, rol tanlang
3. Ixtiyoriy: 2FA majburiy qiling

## ETL boshqaruvi

- Dashboard → ETL Monitor
- Manual trigger: "ETL hozir ishga tushir"
- Log: oxirgi 100 ish

## Backup

- Avtomatik: kuniga 03:00 (Celery beat)
- Saqlanadi: S3 (`s3://backups/oltp/`)
- 30 kundan eski backuplar avtomatik o'chiriladi
