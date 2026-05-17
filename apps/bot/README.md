# UniAnalytics PRO — Telegram Bot

aiogram 3 asosida qurilgan alohida bot xizmati. Backend REST API'siga
HTTP orqali murojaat qiladi (DB ga to'g'ridan-to'g'ri kirmaydi).

## Texnologiyalar

- **aiogram** 3.13+ — async Telegram Bot framework
- **Redis** — FSM storage + auth token cache + throttling
- **httpx** — backend API klienti
- **Pydantic v2** + pydantic-settings — sozlamalar
- **loguru** — strukturalangan loglar

## Arxitektura

```
bot/
├── main.py              # Entry — Bot, Dispatcher, polling/webhook
├── config.py            # .env dan sozlamalar
├── handlers/
│   ├── start.py         # /start, /menu, /help
│   ├── auth.py          # /login (FSM), /logout
│   ├── data.py          # /gpa, /grades, /rank, /schedule, /notifications, /profile
│   └── common.py        # Fallback
├── middlewares/
│   ├── auth.py          # chat_id → token, har bir handlerga `token` qo'shadi
│   └── throttling.py    # Per-user Redis rate limit (default: 20/min)
├── states/
│   └── auth_states.py   # LoginStates(username, password)
├── keyboards/
│   ├── reply.py         # Main menu + cancel
│   └── inline.py        # Pagination + logout confirm
├── services/
│   ├── api_client.py    # Backend HTTP klienti (httpx)
│   └── auth_store.py    # Redis: chat_id ↔ JWT token (7 kun TTL)
└── utils/
    └── formatters.py    # MarkdownV2 escape, grade emoji, weekday
```

## Buyruqlar

### Umumiy
- `/start` — botni boshlash
- `/help` — buyruqlar ro'yxati
- `/menu` — asosiy menyu (reply keyboard)

### Auth
- `/login` — FSM bilan login flow (username → password → token Redis'da saqlanadi)
- `/logout` — chiqish (inline confirm)

### Ma'lumotlar (auth talab qiladi)
- `/gpa` — GPA, o'rtacha ball, davomat, o'tgan/o'tmagan, reyting
- `/grades` — baholar (inline pagination, 10 tadan)
- `/rank` — guruhda o'rin
- `/schedule` — dars jadvali kunlar bo'yicha
- `/notifications` — so'nggi 10 ta bildirishnoma
- `/profile` — shaxsiy ma'lumotlar

## Ishga tushirish

### 1. Bot token olish
[@BotFather](https://t.me/BotFather) → `/newbot` → token nusxa olish.

### 2. `.env` yaratish
```bash
cp .env.example .env
# va TELEGRAM_BOT_TOKEN, BACKEND_API_URL, REDIS_URL ni to'ldiring
```

### 3. Lokal ishga tushirish
```bash
pip install -r requirements.txt
python -m bot.main
```

### 4. Docker
```bash
docker build -t unianalytics-bot .
docker run --rm --env-file .env unianalytics-bot
```

### 5. Docker Compose (asosiy `docker-compose.yml` da)
```yaml
bot:
  build: ./apps/bot
  env_file: ./apps/bot/.env
  depends_on: [backend, redis]
  restart: unless-stopped
```

## Rejimlar

### Polling (default, dev uchun)
`.env`: `BOT_MODE=polling`

### Webhook (production)
```bash
BOT_MODE=webhook
WEBHOOK_URL=https://example.com/webhook
WEBHOOK_SECRET=random-string-here
WEBAPP_HOST=0.0.0.0
WEBAPP_PORT=8080
```

## Xavfsizlik

- Foydalanuvchi parolini kiritgach, bot uni chatdan o'chirishga harakat qiladi
  (`message.delete()`)
- Tokenlar Redis'da 7 kunlik TTL bilan saqlanadi
- 401 javobida foydalanuvchidan qayta login so'raladi
- Throttling: daqiqada 20 ta so'rov (Redis token bucket)
- Webhook secret token tekshiruvi

## Backend integratsiyasi

Bot backendga to'g'ridan-to'g'ri DB orqali kirmaydi — barcha so'rovlar
backend REST API'si orqali ketadi (`/auth/login`, `/auth/me`, `/my/dashboard`,
`/grades`, `/schedule/my`, `/notifications`).

Bu microservices arxitekturasini qo'llab-quvvatlaydi: bot mustaqil deploy
qilinishi mumkin, backend versiyasi o'zgarganda faqat API contract ahamiyatli.

## Mavjud (eski) implementatsiya bilan farqi

| Element              | Eski (`backend/app/services/telegram_bot.py`) | Yangi (`apps/bot/`) |
|----------------------|----------------------------------------------|----------------------|
| Framework            | httpx (raw)                                  | aiogram 3           |
| DB                   | To'g'ridan-to'g'ri SQLAlchemy                | Backend HTTP API     |
| Link storage         | JSON fayl                                    | Redis (JWT bilan)    |
| Auth                 | `/link <student_id>` (xavfsiz emas)          | `/login` FSM         |
| FSM                  | Yo'q                                         | Redis-backed FSM     |
| Throttling           | Yo'q                                         | Token bucket         |
| Pagination           | Yo'q                                         | Inline keyboards     |
| Webhook              | Yo'q                                         | Bor                  |
| Code structure       | Bitta fayl                                   | Modulli routerlar    |

## Kelajak

- [ ] FCM stilida backend → bot bildirishnomalari (Celery'dan, Redis chat_id orqali)
- [ ] Inline grafikalar (matplotlib → PNG → sendPhoto)
- [ ] AI fan tavsiyalari (eski `get_student_recommendations` bilan integrate)
- [ ] Multi-tilli (uz/ru/en — tilni profilga bog'lash)
