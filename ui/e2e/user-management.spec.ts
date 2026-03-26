import { test, expect } from '@playwright/test'

import { loginAsAdmin } from './helpers/auth'

test.describe('User Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/system/user')
  })

  test('should navigate to the user management page', async ({ page }) => {
    await expect(page).toHaveURL(/\/admin\/system\/user(?:$|\?|\/)/)
    await expect(page.getByRole('heading', { name: 'User' })).toBeVisible()
  })

  test('should display the user table and create control', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'Create User' })).toBeVisible()
    await expect(page.locator('.app-table')).toBeVisible()
  })
})
