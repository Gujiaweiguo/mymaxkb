import { test, expect } from '@playwright/test'

const ADMIN_LOGIN_URL = /\/admin\/login(?:$|\?|\/)/
const CHAT_BASE = process.env.E2E_CHAT_BASE_URL || 'http://localhost:3001'

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

  test('should redirect /chat/.html to chat root instead of showing 404', async ({ page }) => {
    await page.goto(`${CHAT_BASE}/chat/.html`)
    await page.waitForLoadState('networkidle')

    await expect(page).not.toHaveURL(/\/chat\/\.html$/)
  })

  test('should serve chat on /chat.html without 404', async ({ page }) => {
    await page.goto(`${CHAT_BASE}/chat.html`)
    await page.waitForLoadState('networkidle')

    await expect(page).not.toHaveURL(/\/404(?:$|\?|\/)/)
  })
})
