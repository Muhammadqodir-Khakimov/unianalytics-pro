# Docusaurus deploy guide

## 1. Local spin-up

```bash
# Bir martalik: yangi Docusaurus loyiha yaratish
cd docs
npx create-docusaurus@latest site classic --typescript

# `site/docusaurus.config.js` ni biz yozganini bilan almashtiring
# `site/docs/` ichiga bizning markdown'larni ko'chiring (avtomatik mavjud)

cd site
npm install
npm run start    # http://localhost:3000
```

## 2. GitHub Pages (eng oson, bepul)

`.github/workflows/docs.yml`:

```yaml
name: Deploy Docs
on:
  push:
    branches: [main]
    paths: ['docs/site/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions: { contents: write }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: |
          cd docs/site
          npm install
          npm run build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/site/build
          cname: docs.unianalytics.uz
```

GitHub Repo → Settings → Pages → Source = "gh-pages branch"
DNS: `docs.unianalytics.uz` CNAME → `<your-github-username>.github.io`

## 3. Vercel (CI/CD avtomatik)

```bash
npm i -g vercel
cd docs/site
vercel
```

`vercel.json` ga (root'da):
```json
{
  "buildCommand": "cd docs/site && npm install && npm run build",
  "outputDirectory": "docs/site/build",
  "framework": null
}
```

Custom domain: Vercel UI → Settings → Domains → `docs.unianalytics.uz`

## 4. Self-hosted (Nginx + Cloudflare)

```bash
cd docs/site
npm run build
rsync -avz build/ user@server:/var/www/docs.unianalytics.uz/
```

`/etc/nginx/sites-available/docs`:
```nginx
server {
    listen 443 ssl http2;
    server_name docs.unianalytics.uz;
    root /var/www/docs.unianalytics.uz;
    index index.html;
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## 5. Multi-language deploy

Docusaurus i18n config'da `uz`, `ru`, `en`, `qq` yoqilgan.
Har bir til alohida URL'da:
- `docs.unianalytics.uz/` (uz — default)
- `docs.unianalytics.uz/ru/`
- `docs.unianalytics.uz/en/`
- `docs.unianalytics.uz/qq/`

Tarjima fayllar `docs/site/i18n/{lang}/...` ichida joylashadi.

```bash
# Tarjima fayllarini avtomatik yaratish
npm run write-translations -- --locale ru
npm run write-translations -- --locale en
npm run write-translations -- --locale qq
```

## 6. Algolia DocSearch (bepul izlash)

```bash
# Ariza: https://docsearch.algolia.com/apply
# Tasdiqlangach .env ga:
ALGOLIA_APP_ID=xxx
ALGOLIA_API_KEY=xxx
ALGOLIA_INDEX_NAME=unianalytics
```

`docusaurus.config.js` → `themeConfig.algolia`.

## 7. Analytics

- **Plausible (GDPR-friendly):** `script tag` qo'shing `<head>` ga
- **Google Analytics:** `@docusaurus/preset-classic` → `gtag` plugin

## Tavsiya yo'l xaritasi

1. **Birinchi qadam:** GitHub Pages (bepul, oson)
2. **Trafik o'sganda:** Vercel yoki Cloudflare Pages
3. **Self-hosted:** Faqat juda katta o'lcham yoki maxsus talab bo'lganda
