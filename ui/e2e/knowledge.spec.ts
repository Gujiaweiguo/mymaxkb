import { test, expect } from '@playwright/test'

test.describe('Knowledge Base Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[placeholder*="username"]', 'admin')
    await page.fill('input[placeholder*="password"]', 'TestPassword123!')
    await page.click('button:has-text("Login")')
    await page.waitForURL(/.*dashboard/)
  })

  test('should navigate to knowledge base', async ({ page }) => {
    await page.click('a:has-text("Knowledge")')
    await expect(page).toHaveURL(/.*knowledge/)
  })

  test('should display knowledge list', async ({ page }) => {
    await page.click('a:has-text("Knowledge")')
    await expect(page.locator('.knowledge-list')).toBeVisible()
  })

  test('should create new knowledge base', async ({ page }) => {
    await page.click('a:has-text("Knowledge")')
    await page.click('button:has-text("Create")')

    await page.fill('input[placeholder*="name"]', 'Test Knowledge')
    await page.fill('textarea[placeholder*="description"]', 'Test Description')
    await page.click('button:has-text("Save")')

    await expect(page.locator('text=Test Knowledge')).toBeVisible()
  })

  test('should upload document to knowledge base', async ({ page }) => {
    await page.click('a:has-text("Knowledge")')
    await page.click('.knowledge-item:has-text("Test Knowledge")')
    await page.click('button:has-text("Upload")')

    const fileInput = page.locator('input[type="file"]')
    await fileInput.setInputFiles('ui/e2e/fixtures/test-document.txt')

    await page.click('button:has-text("Upload")')

    await expect(page.locator('text=test-document.txt')).toBeVisible()
  })

  test('should search knowledge documents', async ({ page }) => {
    await page.click('a:has-text("Knowledge")')
    await page.click('.knowledge-item:has-text("Test Knowledge")')
    await page.fill('input[placeholder*="Search"]', 'test')

    await expect(page.locator('.search-results')).toBeVisible()
  })
})
