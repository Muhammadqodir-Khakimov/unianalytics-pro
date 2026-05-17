import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('login page is reachable', async ({ page }) => {
    await page.goto('/login');
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole('button', { name: /kirish|login|войти/i })).toBeVisible({ timeout: 10000 });
  });

  test('login form requires both fields', async ({ page }) => {
    await page.goto('/login');
    await page.getByRole('button', { name: /kirish|login|войти/i }).click();
    // Should not navigate (still on /login due to validation)
    await page.waitForTimeout(500);
    expect(page.url()).toContain('/login');
  });

  test('admin login → dashboard', async ({ page }) => {
    await page.goto('/login');
    const usernameInput = page.locator('input').first();
    const passwordInput = page.locator('input[type="password"]');
    await usernameInput.fill('admin');
    await passwordInput.fill('admin123');
    await page.getByRole('button', { name: /kirish|login|войти/i }).click();
    await page.waitForURL(/\/dashboard|\/$|\/landing/, { timeout: 15000 }).catch(() => {});
    // Either dashboard or we're still logged in somewhere
    expect(page.url()).not.toContain('/login');
  });
});
