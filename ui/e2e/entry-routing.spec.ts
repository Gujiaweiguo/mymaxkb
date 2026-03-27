import { test, expect } from '@playwright/test'

const ADMIN_LOGIN_URL = /\/admin\/login(?:$|\?|\/)/
const CHAT_CANONICAL_URL = /\/chat\.html(?:$|\?)/

test.describe('Entry path normalization', () => {
  test('should redirect /admin/.html to admin login instead of showing 404', async ({ page }) => {
    await page.goto('/admin/.html')
    await page.waitForLoadState('networkidle')

    await expect(page).not.toHaveURL(/\/admin\/\.html$/)
    await expect(page.locator('.not-found-container')).toHaveCount(0)
    await expect(page.getByPlaceholder('Please enter username')).toBeVisible()
    await expect(page.getByPlaceholder('Please enter password')).toBeVisible()
  })

  test('should redirect /admin.html to admin login', async ({ page }) => {
    await page.goto('/admin.html')
    await page.waitForLoadState('networkidle')

    await expect(page).toHaveURL(ADMIN_LOGIN_URL)
    await expect(page.getByPlaceholder('Please enter username')).toBeVisible()
    await expect(page.getByPlaceholder('Please enter password')).toBeVisible()
  })

  test('should redirect /chat/.html to canonical chat entry', async ({ page }) => {
    await page.goto('/chat/.html')
    await page.waitForLoadState('networkidle')

    await expect(page).not.toHaveURL(/\/chat\/\.html$/)
    await expect(page.locator('.not-found-container')).toHaveCount(0)
  })

  test('should serve chat on /chat.html without redirect loop', async ({ page }) => {
    await page.goto('/chat.html')
    await page.waitForLoadState('networkidle')

    await expect(page).toHaveURL(CHAT_CANONICAL_URL)
    await expect(page.locator('.not-found-container')).toHaveCount(0)
  })
})
