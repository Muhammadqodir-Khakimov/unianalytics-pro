# Sentry sozlamasi

## Backend

```env
SENTRY_DSN=https://...@o123.ingest.sentry.io/456
APP_VERSION=v1.0.0          # yoki GIT_SHA bilan auto
APP_ENV=production
SENTRY_TRACES_RATE=0.1
SENTRY_PROFILES_RATE=0.1
```

## Frontend

```env
VITE_SENTRY_DSN=https://...@o123.ingest.sentry.io/789
VITE_APP_VERSION=v1.0.0
VITE_APP_ENV=production
```

`main.tsx` ga:
```ts
import { initSentry } from './sentry';
initSentry();
```

## Source-map upload (CI'da)

```bash
npm i -g @sentry/cli

# Build
npm run build

# Upload source maps
sentry-cli releases new "unianalytics-frontend@$GIT_SHA"
sentry-cli releases files "unianalytics-frontend@$GIT_SHA" \
  upload-sourcemaps ./dist --url-prefix '~/assets'
sentry-cli releases finalize "unianalytics-frontend@$GIT_SHA"

# Source-maplar Sentry'ga yuklanganidan keyin dist'dan o'chirib tashlash
find dist -name "*.map" -delete
```

## GitHub Actions snippet

```yaml
- name: Sentry release
  env:
    SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
    SENTRY_ORG: unianalytics
    SENTRY_PROJECT: frontend
  run: |
    npx @sentry/cli releases new "$GITHUB_SHA"
    npx @sentry/cli releases files "$GITHUB_SHA" upload-sourcemaps ./dist
    npx @sentry/cli releases finalize "$GITHUB_SHA"
```
