import { test, expect } from '@playwright/test'

test.describe('Workspace Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[placeholder*="username"]', 'admin')
    await page.fill('input[placeholder*="password"]', 'TestPassword123!')
    await page.click('button:has-text("Login")')
    await page.waitForURL(/.*dashboard/)
  })

  test('should navigate to workspace settings', async ({ page }) => {
    await page.click('a:has-text("Settings")')
    await page.click('a:has-text("Workspace")')
    await expect(page).toHaveURL(/.*workspace/)
  })

  test('should display workspace list', async ({ page }) => {
    await page.click('a:has-text("Settings")')
    await page.click('a:has-text("Workspace")')
    await expect(page.locator('table')).toBeVisible()
  })

  test('should create new workspace', async ({ page }) => {
    await page.click('a:has-text("Settings")')
    await page.click('a:has-text("Workspace")')
    await page.click('button:has-text("Create")')

    await page.fill('input[placeholder*="name"]', 'Test Workspace')
    await page.click('button:has-text("Save")')

    await expect(page.locator('text=Test Workspace')).toBeVisible()
  })

  test('should switch workspace', async ({ page }) => {
    await page.click('[data-testid="workspace-selector"]')
    await page.click('text=Test Workspace')

    await expect(page.locator('[data-testid="current-workspace"]')).toContainText('Test Workspace')
  })
})
