import { test, expect } from '@playwright/test'

test.describe('Login Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
  })

  test('should display login form', async ({ page }) => {
    await expect(page.locator('input[placeholder*="username"]')).toBeVisible()
    await expect(page.locator('input[placeholder*="password"]')).toBeVisible()
    await expect(page.locator('button:has-text("Login")')).toBeVisible()
  })

  test('should login with valid credentials', async ({ page }) => {
    await page.fill('input[placeholder*="username"]', 'admin')
    await page.fill('input[placeholder*="password"]', 'TestPassword123!')
    await page.click('button:has-text("Login")')

    await expect(page).toHaveURL(/.*dashboard/)
  })

  test('should show error with invalid credentials', async ({ page }) => {
    await page.fill('input[placeholder*="username"]', 'admin')
    await page.fill('input[placeholder*="password"]', 'WrongPassword')
    await page.click('button:has-text("Login")')

    await expect(page.locator('.error-message')).toBeVisible()
  })

  test('should show validation for empty fields', async ({ page }) => {
    await page.click('button:has-text("Login")')

    await expect(page.locator('.error-message')).toBeVisible()
  })
})
