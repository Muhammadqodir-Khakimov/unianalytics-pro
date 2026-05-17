# Security Notes

## npm audit holati (2026-05-17 yangilangan)

| Paket | Severity | Status | Sabab |
|-------|----------|--------|-------|
| xlsx | high | **OLIB TASHLANDI** | Hech qaerda ishlatilmagan, server-side Excel generation |
| jspdf | critical | **OLIB TASHLANDI** | Server-side PDF generation orqali almashtirildi |
| esbuild (Vite 5 dev server) | moderate | **PROD'GA TA'SIR ETMAYDI** | Faqat dev server bug — prod bundle xavfsiz |

## Vite dev server vulnerability

`esbuild < 0.24.2` da dev server orqali boshqa veb-saytlar request yuborishi mumkin. Lekin:
- Bu faqat **lokal dev** (`npm run dev`) ishlayotganda
- Prod build (`npm run build`) bunga ta'sir qilmaydi (esbuild faqat build-time)
- Hech qachon dev server'ni public internet'ga ochmang

**Yechim:** Dev paytida `vite.config.ts` da `server.host = 'localhost'` (default).

## Production checklist

- [x] HTTPS hamma joyda
- [x] JWT secret env'da (hardcoded emas)
- [x] CORS faqat ma'lum origin'lar
- [x] Rate limiting (slowapi)
- [x] SQL injection — SQLAlchemy ORM ishlatilgan
- [x] XSS — React default escape
- [x] CSRF — token-based auth (cookie emas)
- [x] Parol bcrypt hash
- [x] 2FA mavjud
- [x] Backup encryption (S3 server-side)

## Tavsiya

3 oyda bir marta:
```bash
npm audit
pip-audit -r requirements.txt
```

CI'da automated:
```yaml
- run: npm audit --audit-level=high
- run: pip-audit -r requirements.txt
```
