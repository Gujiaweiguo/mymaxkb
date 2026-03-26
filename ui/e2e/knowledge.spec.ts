import { test, expect } from '@playwright/test'

import { loginAsAdmin } from './helpers/auth'

test.describe('Knowledge Base Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/knowledge')
  })

  test('should navigate to the knowledge page', async ({ page }) => {
    await expect(page).toHaveURL(/\/admin\/knowledge(?:$|\?|\/)/)
    await expect(page.locator('.knowledge-manage')).toBeVisible()
  })

  test('should display knowledge heading and create control', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Knowledge' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Create' })).toBeVisible()
  })
})
