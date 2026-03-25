import { test, expect } from '@playwright/test'

test.describe('User Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[placeholder*="username"]', 'admin')
    await page.fill('input[placeholder*="password"]', 'TestPassword123!')
    await page.click('button:has-text("Login")')
    await page.waitForURL(/.*dashboard/)
  })

  test('should navigate to user management', async ({ page }) => {
    await page.click('a:has-text("User Management")')
    await expect(page).toHaveURL(/.*user-manage/)
  })

  test('should display user list', async ({ page }) => {
    await page.click('a:has-text("User Management")')
    await expect(page.locator('table')).toBeVisible()
  })

  test('should create new user', async ({ page }) => {
    await page.click('a:has-text("User Management")')
    await page.click('button:has-text("Create User")')

    await page.fill('input[placeholder*="username"]', 'newuser')
    await page.fill('input[placeholder*="email"]', 'newuser@example.com')
    await page.fill('input[placeholder*="password"]', 'NewUser123!')
    await page.click('button:has-text("Save")')

    await expect(page.locator('text=newuser')).toBeVisible()
  })

  test('should search users', async ({ page }) => {
    await page.click('a:has-text("User Management")')
    await page.fill('input[placeholder*="Search"]', 'admin')

    await expect(page.locator('text=admin')).toBeVisible()
  })

  test('should delete user', async ({ page }) => {
    await page.click('a:has-text("User Management")')

    await page.click('button:has-text("Delete")')
    await page.click('button:has-text("Confirm")')

    await expect(page.locator('text=User deleted')).toBeVisible()
  })
})
