import { test, expect } from '@playwright/test';

async function login(page: any) {
  await page.goto('/login');
  await page.locator('input').first().fill('admin');
  await page.locator('input[type="password"]').fill('admin123');
  await page.getByRole('button', { name: /kirish|login|войти/i }).click();
  await page.waitForURL((u: URL) => !u.pathname.includes('/login'), { timeout: 15000 });
}

test.describe('Dashboard (authenticated)', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('dashboard renders KPI cards', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.locator('.ant-card').first()).toBeVisible({ timeout: 10000 });
  });

  test('sidebar navigation works', async ({ page }) => {
    await page.goto('/dashboard');
    // Click students from menu
    const studentsLink = page.locator('a[href*="/students"]').first();
    if (await studentsLink.isVisible()) {
      await studentsLink.click();
      await page.waitForURL(/\/students/);
      expect(page.url()).toContain('/students');
    }
  });
});
