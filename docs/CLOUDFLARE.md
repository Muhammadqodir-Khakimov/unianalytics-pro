# Cloudflare CDN & Security Setup

## 1. Cloudflare hisob

1. https://dash.cloudflare.com/sign-up
2. Domenni qo'shing: `unianalytics.uz`
3. Cloudflare beradi 2 ta nameserver — domen registrar (name.uz) da nameserver larni o'zgartiring

## 2. DNS sozlash

Cloudflare → DNS:
- A record: `unianalytics.uz` → Railway/server IP (proxied — orange cloud)
- A record: `*.unianalytics.uz` → Railway IP (proxied)
- CNAME: `www` → `unianalytics.uz`

## 3. SSL

Cloudflare → SSL/TLS → **Full (strict)**

Origin sertifikat:
1. Cloudflare → SSL/TLS → Origin Server → Create Certificate
2. Nginx/Railway ga origin cert qo'shing

## 4. Performance

- **Caching:** Page Rules ga `*.unianalytics.uz/assets/*` uchun "Cache Everything"
- **Auto Minify:** JS, CSS, HTML ni yoqing
- **Brotli:** yoqing
- **Rocket Loader:** test rejimida

## 5. Security

- **Bot Fight Mode:** ON
- **WAF Rules:** OWASP ruleset ON
- **Rate Limiting:** 10 req/min har IP uchun login endpoint
- **DDoS Protection:** ON (auto)

## 6. Analytics

Cloudflare Analytics — bepul. Plausible.io (paid, GDPR-friendly).

## Narx

- **Free plan:** Yetarli (basic CDN, SSL, WAF)
- **Pro plan:** $25/oy (advanced WAF, image optimization)
