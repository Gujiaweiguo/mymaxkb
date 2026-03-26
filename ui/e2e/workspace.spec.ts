import { test, expect } from '@playwright/test'

import { loginAsAdmin } from './helpers/auth'

test.describe('Workspace Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/system/workspace')
  })

  test('should navigate to the workspace page', async ({ page }) => {
    await expect(page).toHaveURL(/\/admin\/system\/workspace(?:$|\?|\/)/)
    await expect(page.locator('.workspace-manage')).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Workspace', exact: true })).toBeVisible()
  })

  test('should display workspace panels and search input', async ({ page }) => {
    await expect(page.locator('.workspace-left')).toBeVisible()
    await expect(page.locator('.workspace-right')).toBeVisible()
    await expect(page.getByPlaceholder('Search')).toBeVisible()
  })
})
