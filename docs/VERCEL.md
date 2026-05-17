# Vercel deploy yo'riqnomasi (frontend uchun)

ReytingOLAP frontend (React + Vite + Ant Design) Vercel'da joylashtiriladi.
Backend, bot, DB va Redis esa Railway'da qoladi.

```
Vercel              ┌────────► Railway (backend, bot, OLTP, OLAP, Redis)
(frontend)  ── HTTPS ┘          └── Telegram users (bot polling)
   ▲
   │
Foydalanuvchilar
```

---

## 1. Vercel loyiha yaratish

### A) Dashboard orqali (eng oson)

1. https://vercel.com/new — GitHub repo'ni import qiling: `Muhammadqodir-Khakimov/unianalytics-pro`
2. **Configure Project** sahifasida:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`  ← **muhim**
   - **Build Command**: avtomatik (`npm run build`)
   - **Output Directory**: avtomatik (`dist`)
3. **Environment Variables** bo'limida qo'shing:
   - `VITE_API_BASE_URL` = `https://<backend>.up.railway.app/api/v1`
4. **Deploy** tugmasini bosing.

### B) CLI orqali

```powershell
npm i -g vercel
cd frontend
vercel login
vercel link              # mavjud loyihaga yoki yangi yaratish
vercel env add VITE_API_BASE_URL production
# Qiymat: https://<backend>.up.railway.app/api/v1
vercel --prod
```

Yoki bir buyruq bilan (deploy skript orqali):

```powershell
.\scripts\deploy_vercel.ps1 -BackendUrl "https://<backend>.up.railway.app"
```

---

## 2. Environment variables (Vercel)

Vercel dashboard → **Settings → Environment Variables**.

| Variable | Production qiymati | Preview qiymati |
|---|---|---|
| `VITE_API_BASE_URL` | `https://<backend-prod>.up.railway.app/api/v1` | shu qiymat (yoki staging URL) |
| `VITE_APP_NAME` | `ReytingOLAP` | shu |
| `VITE_DEFAULT_LANG` | `uz` | shu |

> Vite env'lari `VITE_` prefiksi bilan, build paytida bundle'ga "baked in" bo'ladi — qayta deploy kerak.

---

## 3. Backend CORS (Railway tomonida)

Backend kod allaqachon `*.vercel.app` regex'ini default'da ruxsat etadi (`config.cors_origin_regex`). Lekin **production exact domain** ham qo'shilishi tavsiya etiladi:

Railway dashboard → backend service → **Variables**:

```
CORS_ORIGINS=https://unianalytics.vercel.app,https://www.unianalytics.uz
```

Custom domeningiz bo'lsa, uni ham qo'shing.

Vercel preview deploy'lari uchun (har commit'da yangi URL) — `CORS_ORIGIN_REGEX` default'i avtomatik:
```
https://([a-z0-9-]+\.)?(vercel\.app|up\.railway\.app)
```

Custom regex xohlasangiz `CORS_ORIGIN_REGEX` env'iga to'g'ridan-to'g'ri qiymat bering.

---

## 4. Custom domen ulanishi (ixtiyoriy)

1. Vercel dashboard → **Settings → Domains**
2. `unianalytics.uz` (yoki sizning domeningiz) kiriting
3. DNS provider'da CNAME yozuv: `unianalytics.uz` → `cname.vercel-dns.com`
4. SSL avtomatik (Let's Encrypt)
5. Backend `CORS_ORIGINS` ga yangi domeni qo'shing

---

## 5. Vercel.json konfiguratsiyasi

`frontend/vercel.json` allaqachon yaratilgan. Asosiy nuqtalar:

- **SPA routing**: `/(.*)  → /index.html` (React Router uchun)
- **Asset cache**: `/assets/*` → 1 yil immutable
- **Security headers**: X-Frame-Options, X-Content-Type-Options, Permissions-Policy
- **Build**: Vite framework, `npm ci` + `npm run build`

---

## 6. Avtomatik deploy GitHub orqali

Vercel git integratsiyasi sukut bo'yicha:
- `main` branch → production deploy
- Boshqa branch'lar → preview deploy (har biri o'z URL'iga)
- Pull Request'lar → avtomatik preview + PR comment

Hech narsa qo'shish shart emas.

---

## 7. Tipik xatolar

| Xato | Yechim |
|---|---|
| `CORS error: blocked by policy` | Railway backend'da `CORS_ORIGINS` ga Vercel domenni qo'shing va backend qayta deploy |
| `404 on page refresh` | `vercel.json` rewrites'ni tekshiring (`/(.*) -> /index.html`) |
| `Build failed: cannot find module` | `Root Directory = frontend` ekanligini tekshiring |
| `Env var not in bundle` | Vite env `VITE_` prefiksi shart, build qayta ishga tushirilsin |
| `Mixed content (http)` | Backend HTTPS bo'lishi shart (Railway avtomatik beradi) |
| Preview deploy'da API ishlamaydi | `VITE_API_BASE_URL` ni Preview environment uchun ham o'rnating |

---

## 8. Stack umumiy ko'rinishi

| Komponent | Hosting | URL namuna |
|---|---|---|
| Frontend (SPA) | **Vercel** | `https://unianalytics.vercel.app` |
| Backend API | Railway | `https://backend.up.railway.app` |
| Telegram bot | Railway (worker) | (URL kerakmas, polling) |
| Postgres OLTP | Railway plugin | `${{Postgres-OLTP.DATABASE_URL}}` |
| Postgres OLAP | Railway plugin | `${{Postgres-OLAP.DATABASE_URL}}` |
| Redis | Railway plugin | `${{Redis.REDIS_URL}}` |

Backend deploy bo'yicha: [`docs/RAILWAY.md`](./RAILWAY.md)
