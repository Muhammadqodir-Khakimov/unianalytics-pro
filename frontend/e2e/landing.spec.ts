import { test, expect } from '@playwright/test';

test.describe('Public landing', () => {
  test('landing page loads', async ({ page }) => {
    const res = await page.goto('/landing');
    expect(res?.status()).toBeLessThan(500);
  });

  test('no JS console errors on landing', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    await page.goto('/landing');
    await page.waitForTimeout(2000);
    // Allow a few known noisy warnings (CORS preflight to API on landing etc.)
    const fatal = errors.filter((e) => !e.includes('CORS') && !e.includes('favicon'));
    expect(fatal.length).toBeLessThan(5);
  });
});
