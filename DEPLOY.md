# 🚀 Deployment Yo'riqnomasi

UniAnalytics PRO ni 4 xil platformaga deploy qilish.

## 📋 Tezkor variantlar

| Platform | Narx | Setup vaqti | Tavsiya |
|----------|------|-------------|---------|
| **Railway** | $5-20/oy | 5 daqiqa | ⭐ Boshlash uchun |
| **Render** | $0-25/oy | 10 daqiqa | Free tier bor |
| **Fly.io** | $2-15/oy | 15 daqiqa | Global edge |
| **VPS (Hetzner)** | $5-30/oy | 1 soat | To'liq nazorat |

---

## 🚂 Railway (eng oson)

### 1. GitHub repo
```bash
gh repo create unianalytics-pro --public
git push -u origin main
```

### 2. Railway setup
1. https://railway.app ga kiring (GitHub orqali)
2. "New Project" → "Deploy from GitHub repo"
3. unianalytics-pro ni tanlang
4. Railway avtomatik `railway.json` ni o'qiydi

### 3. Database qo'shish
- "New" → "Database" → "PostgreSQL" (OLTP uchun)
- Yana "PostgreSQL" (OLAP uchun)
- "Redis" (cache)

### 4. Environment variables
Backend service ga:
```
OLTP_DB_URL=${{Postgres-OLTP.DATABASE_URL}}
OLAP_DB_URL=${{Postgres-OLAP.DATABASE_URL}}
REDIS_HOST=${{Redis.REDIS_HOST}}
REDIS_PORT=${{Redis.REDIS_PORT}}
SECRET_KEY=your-strong-secret-key
APP_ENV=production
APP_DEBUG=false
```

### 5. Deploy
Railway avtomatik build qiladi. Tugagach domain link beradi.

---

## 🎨 Render

### 1. render.yaml mavjud
Loyihangizda `render.yaml` allaqachon bor.

### 2. Setup
1. https://render.com ga kiring
2. "New" → "Blueprint"
3. GitHub repo ni tanlang
4. render.yaml avtomatik aniqlanadi
5. "Apply"

### 3. Env vars
Render dashboard'da har bir service uchun env vars ni qo'shing (yoki Generate orqali).

---

## ✈️ Fly.io

### 1. CLI install
```bash
curl -L https://fly.io/install.sh | sh
fly auth login
```

### 2. fly.toml yaratish
```bash
cd backend
fly launch --no-deploy
```

### 3. Postgres qo'shish
```bash
fly postgres create --name unianalytics-oltp
fly postgres attach unianalytics-oltp
```

### 4. Deploy
```bash
fly deploy
```

---

## 🖥️ VPS (Hetzner/DigitalOcean)

### 1. Server tayyorlash
```bash
ssh root@your-server-ip

# Docker o'rnatish
curl -fsSL https://get.docker.com | sh
apt install docker-compose-plugin -y

# Loyihani klonlash
git clone https://github.com/YOUR_USERNAME/unianalytics-pro
cd unianalytics-pro
```

### 2. .env tayyorlash
```bash
cp backend/.env.production.example backend/.env.production
nano backend/.env.production
# Parollarni o'zgartiring!
```

### 3. SSL sertifikat
```bash
# Certbot
apt install certbot -y
certbot certonly --standalone -d unianalytics.uz -d *.unianalytics.uz
cp /etc/letsencrypt/live/unianalytics.uz/*.pem nginx/ssl/
```

### 4. Ishga tushirish
```bash
docker compose -f docker-compose.prod.yml up -d
```

### 5. Domain DNS
- A record: unianalytics.uz → server IP
- Wildcard: *.unianalytics.uz → server IP (sub-tenant lar uchun)

---

## 🔐 Production checklist

- [ ] **SECRET_KEY** kuchli random string (64+ belgi)
- [ ] DB parollar o'zgartirilgan
- [ ] Redis parol o'rnatilgan
- [ ] CORS_ORIGINS faqat haqiqiy domen
- [ ] SSL sertifikat (Let's Encrypt)
- [ ] Backup avtomatik (cron + S3)
- [ ] Sentry DSN o'rnatilgan
- [ ] Telegram bot token (xato xabarlari uchun)
- [ ] Eskiz SMS sozlamalari
- [ ] Click/Payme merchant ID
- [ ] Rate limiting yoqilgan
- [ ] Logs strukturali (JSON)
- [ ] Monitoring (Uptime Robot/Pingdom)

---

## 📊 Monitoring URLlar

| Servis | URL |
|--------|-----|
| Frontend | https://yourdomain.uz |
| API | https://yourdomain.uz/api |
| Swagger | https://yourdomain.uz/docs |
| Metrics | https://yourdomain.uz/metrics |
| Flower | https://yourdomain.uz/flower |

---

## 🔄 Auto deploy GitHub Actions orqali

`.github/workflows/deploy.yml` allaqachon sozlangan. Faqat secrets qo'shing:

GitHub repo → Settings → Secrets:
- `RAILWAY_TOKEN` (Railway dashboard'dan)
- `RENDER_DEPLOY_HOOK` (Render service settings'dan)
- `TELEGRAM_BOT_TOKEN` (bildirgilar uchun)
- `TELEGRAM_CHAT_ID`

Har `git push main` da avtomatik deploy bo'ladi.

---

## 🆘 Muammolar

### Backend ishga tushmadi
```bash
docker compose -f docker-compose.prod.yml logs backend
```

### Database ulanmadi
- DATABASE_URL to'g'ri formatda ekanligini tekshiring
- Network/firewall

### Frontend 502
- Backend salomatligini tekshiring: `/health`
- Nginx upstream konfiguratsiya
- CORS_ORIGINS to'g'ri sozlanganmi

---

## 💰 Tahminiy oylik xarajat (Year 1)

| Item | Narx |
|------|------|
| Railway / Render | $20/oy |
| Domain (.uz) | $10/yil |
| Cloudflare | Bepul |
| Sentry (free tier) | Bepul |
| OpenAI / Claude API | $20-50/oy |
| Eskiz SMS | $10/oy (1000 SMS) |
| **Jami** | **~$60/oy = $720/yil** |

Year 1 daromad maqsadi: $12,000 → **5,000 dan ortiq sof foyda**

---

## 📞 Yordam

- Discord: discord.gg/anthropic (Claude API)
- Stack Overflow
- GitHub Issues
