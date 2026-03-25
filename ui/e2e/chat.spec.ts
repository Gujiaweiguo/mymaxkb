import { test, expect } from '@playwright/test'

test.describe('Chat Interaction', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[placeholder*="username"]', 'admin')
    await page.fill('input[placeholder*="password"]', 'TestPassword123!')
    await page.click('button:has-text("Login")')
    await page.waitForURL(/.*dashboard/)
  })

  test('should navigate to chat', async ({ page }) => {
    await page.click('a:has-text("Application")')
    await page.click('.application-item:has-text("Test Application")')
    await page.click('button:has-text("Chat")')

    await expect(page).toHaveURL(/.*chat/)
  })

  test('should send message in chat', async ({ page }) => {
    await page.click('a:has-text("Application")')
    await page.click('.application-item:has-text("Test Application")')
    await page.click('button:has-text("Chat")')

    await page.fill('textarea[placeholder*="message"]', 'Hello, how are you?')
    await page.click('button:has-text("Send")')

    await expect(page.locator('.message:has-text("Hello, how are you?")')).toBeVisible()
  })

  test('should receive chat response', async ({ page }) => {
    await page.click('a:has-text("Application")')
    await page.click('.application-item:has-text("Test Application")')
    await page.click('button:has-text("Chat")')

    await page.fill('textarea[placeholder*="message"]', 'Hello')
    await page.click('button:has-text("Send")')

    await page.waitForSelector('.response-message')
    await expect(page.locator('.response-message')).toBeVisible()
  })

  test('should display chat history', async ({ page }) => {
    await page.click('a:has-text("Application")')
    await page.click('.application-item:has-text("Test Application")')
    await page.click('button:has-text("Chat")')

    await expect(page.locator('.chat-history')).toBeVisible()
  })

  test('should vote on chat response', async ({ page }) => {
    await page.click('a:has-text("Application")')
    await page.click('.application-item:has-text("Test Application")')
    await page.click('button:has-text("Chat")')

    await page.fill('textarea[placeholder*="message"]', 'Test question')
    await page.click('button:has-text("Send")')

    await page.waitForSelector('.response-message')
    await page.click('.vote-button:has-text("Thumbs Up")')

    await expect(page.locator('.vote-success')).toBeVisible()
  })
})
