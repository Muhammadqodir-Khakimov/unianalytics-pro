# E2E Tests (Playwright)

## Setup

```bash
npm install
npx playwright install --with-deps
```

## Run

```bash
# Backend va frontend ishlab turishi kerak
# Terminal 1:
cd ../backend && uvicorn app.main:app --reload

# Terminal 2:
npm run dev

# Terminal 3:
npm run test:e2e            # Headless
npm run test:e2e:ui         # Browser UI rejim
```

## CI da

```yaml
- run: npx playwright install --with-deps
- run: npm run test:e2e
  env:
    E2E_BASE_URL: http://localhost:3000
```

## Test fayllar

- `auth.spec.ts` — login form, validation, admin login
- `dashboard.spec.ts` — authenticated routes, sidebar navigation
- `landing.spec.ts` — public landing, console errors

## Yangi test qo'shish

```ts
import { test, expect } from '@playwright/test';

test('my new test', async ({ page }) => {
  await page.goto('/some-route');
  await expect(page.getByRole('heading')).toBeVisible();
});
```
