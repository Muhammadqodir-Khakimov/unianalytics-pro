# Bepul deploy: Netlify + Railway + Upstash + Fly.io

ReytingOLAP'ni butunlay bepul rejimlarda joylashtirish.

## Stack

| Komponent | Provayder | Rejim | Cheklov |
|---|---|---|---|
| **Frontend** | Netlify | Free | Cheksiz traffic, 100 GB build/oy |
| **Backend** | Railway | Trial / Free | 500 soat/oy ish vaqti |
| **Postgres OLTP+OLAP** | Railway | bitta postgres-oltp service, 2 ta DB | 1 GB |
| **Redis** | Upstash | Free | 10K so'rov/kun, 256 MB |
| **Bot** | Fly.io | Free | 3 ta kichik VM (256 MB) |

---

## 1. Netlify (frontend)

### A) GitHub UI orqali (eng oson)
1. https://app.netlify.com → **Add new site → Import an existing project**
2. **GitHub** → `Muhammadqodir-Khakimov/unianalytics-pro` ni tanlang
3. **Build settings** (`netlify.toml`dan o'qiladi):
   - Base directory: `frontend`
   - Build command: `npm ci && npm run build`
   - Publish directory: `frontend/dist`
4. **Environment variables**:
   ```
   VITE_API_BASE_URL = https://backend-production-89be.up.railway.app/api/v1
   VITE_APP_NAME     = ReytingOLAP
   VITE_DEFAULT_LANG = uz
   ```
5. **Deploy site**

### B) CLI orqali
```powershell
npm i -g netlify-cli
netlify login
cd frontend
netlify init           # mavjud loyihaga yoki yangi yaratish
netlify env:set VITE_API_BASE_URL "https://backend-production-89be.up.railway.app/api/v1"
netlify deploy --prod
```

Netlify domeningiz: `https://<sayt-nomi>.netlify.app`

---

## 2. Upstash Redis (bot va backend kesh uchun)

1. https://console.upstash.com → **Create Database**
2. **Name**: `unianalytics-redis`, **Type**: Regional, **Region**: eu-central-1 (Frankfurt)
3. **TLS**: Enabled, **Eviction**: allkeys-lru
4. **Create**

So'ngra **Details → REST API** ko'rinishida ulangan:
- **Endpoint**: `xxxx.upstash.io:6379`
- **Password**: ...
- **Redis URL**: `rediss://default:<password>@<endpoint>:6379` ← bu nusxa oling

URL'ni:
- Railway backend env'iga: `REDIS_URL=rediss://...`
- Fly.io bot env'iga: `REDIS_URL=rediss://...`

---

## 3. Fly.io (Telegram bot)

### Birinchi qadam — CLI o'rnatish va login

```powershell
iwr https://fly.io/install.ps1 -useb | iex
fly auth login        # brauzerda OAuth
```

### Loyihani yaratish va deploy

```powershell
cd apps/bot
fly launch --copy-config --no-deploy --name unianalytics-bot --region fra
# Ha, mavjud fly.toml ni ishlatish
# Ha, sirlar keyin sozlanadi

fly secrets set `
  TELEGRAM_BOT_TOKEN="8433651397:AAEF-..." `
  BACKEND_API_URL="https://backend-production-89be.up.railway.app/api/v1" `
  REDIS_URL="rediss://default:...@xxx.upstash.io:6379"

fly deploy
```

Loglar:
```powershell
fly logs           # real-time
fly status         # ish holati
```

---

## 4. Railway backend yangilash

Yangi Netlify domeningiz va Upstash REDIS_URL'ni Railway backend env'iga qo'shing:

Railway dashboard → `backend` service → **Variables**:
```
CORS_ORIGINS=https://<your-netlify-site>.netlify.app,https://<custom-domain>
REDIS_URL=rediss://default:...@xxx.upstash.io:6379
```

Backend avtomatik qayta deploy bo'ladi.

---

## 5. Yakuniy texologik aloqalar

```
Foydalanuvchilar
   │
   ▼ HTTPS
┌──────────────────┐
│ Netlify          │
│ (frontend SPA)   │
└──────┬───────────┘
       │ HTTPS /api/v1
       ▼
┌──────────────────┐         ┌──────────────────┐
│ Railway backend  │ ◄────── │ Fly.io bot       │
│ FastAPI          │         │ aiogram polling  │
└──────┬───────────┘         └────────┬─────────┘
       │                              │
       ▼                              ▼
   Railway                       Upstash
   postgres-oltp                 Redis
   (unianalytics DB)
                                       ▲
                                       │
                                  Railway backend
                                  (kesh uchun)
```

---

## 6. Bepul rejaning kamchiliklari

- **Railway** — bepul trial 500 soat/oy. Tugasa, kredit kartochka kerak (yoki kichik to'lov)
- **Netlify** — frontend uchun cheksiz, hech qachon tugamaydi
- **Upstash** — 10K so'rov/kun bepul. Talaba+bot uchun yetarli. ~$1/oy keyin
- **Fly.io** — 3 ta kichik VM bepul, ma'lumotlar bazasi alohida hisoblanadi

Akademik BMI uchun **bularning hammasi yetarli**. Real foydalanuvchi traffigi katta bo'lsa, Railway/Render hot tier'ga o'tish kerak ($5–7/oy).

---

## 7. Tipik xatolar

| Xato | Yechim |
|---|---|
| Netlify build "command not found: npm" | Base directory: `frontend` ekanligini tekshiring |
| Frontend CORS error | Railway backend `CORS_ORIGINS` ga Netlify domeni qo'shilganligini va backend qayta deploy bo'lganligini tekshiring |
| Bot ulanmadi | `fly logs` ko'ring — `TELEGRAM_BOT_TOKEN` to'g'riligini va Upstash `REDIS_URL` ishlayotganligini tekshiring |
| Backend 500 / DB error | Railway dashboard → `backend` service → `Variables` da `OLTP_DB_URL`, `OLAP_DB_URL` ko'rsatilgan ekanligini tekshiring |
| Upstash quotani oshib ketsa | Mavjud kalitlarni TTL bilan o'rnatish, kesh hajmini kamaytirish |
