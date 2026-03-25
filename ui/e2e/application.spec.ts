import { test, expect } from '@playwright/test'

test.describe('Application Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[placeholder*="username"]', 'admin')
    await page.fill('input[placeholder*="password"]', 'TestPassword123!')
    await page.click('button:has-text("Login")')
    await page.waitForURL(/.*dashboard/)
  })

  test('should navigate to application list', async ({ page }) => {
    await page.click('a:has-text("Application")')
    await expect(page).toHaveURL(/.*application/)
  })

  test('should display application list', async ({ page }) => {
    await page.click('a:has-text("Application")')
    await expect(page.locator('.application-list')).toBeVisible()
  })

  test('should create new application', async ({ page }) => {
    await page.click('a:has-text("Application")')
    await page.click('button:has-text("Create")')

    await page.fill('input[placeholder*="name"]', 'Test Application')
    await page.fill('textarea[placeholder*="description"]', 'Test Description')
    await page.click('button:has-text("Save")')

    await expect(page.locator('text=Test Application')).toBeVisible()
  })

  test('should edit application', async ({ page }) => {
    await page.click('a:has-text("Application")')
    await page.click('.application-item:has-text("Test Application")')
    await page.click('button:has-text("Edit")')

    await page.fill('input[placeholder*="name"]', 'Updated Application')
    await page.click('button:has-text("Save")')

    await expect(page.locator('text=Updated Application')).toBeVisible()
  })

  test('should delete application', async ({ page }) => {
    await page.click('a:has-text("Application")')
    await page.click('.application-item:has-text("Updated Application")')
    await page.click('button:has-text("Delete")')
    await page.click('button:has-text("Confirm")')

    await expect(page.locator('text=Updated Application')).not.toBeVisible()
  })
})
