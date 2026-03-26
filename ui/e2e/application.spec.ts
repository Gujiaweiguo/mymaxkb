import { test, expect } from '@playwright/test'

import { ADMIN_APPLICATION_URL, loginAsAdmin } from './helpers/auth'

test.describe('Application Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
  })

  test('should land on the application page after login', async ({ page }) => {
    await expect(page).toHaveURL(ADMIN_APPLICATION_URL)
    await expect(page.locator('.application-manage')).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Agent' })).toBeVisible()
  })

  test('should display application search and create controls', async ({ page }) => {
    await expect(page.locator('.application-manage .complex-search')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Create' })).toBeVisible()
  })

  test('should open the create application menu', async ({ page }) => {
    await page.getByRole('button', { name: 'Create' }).click()

    await expect(page.getByText('Simple Agent', { exact: true })).toBeVisible()
    await expect(page.getByText('Advanced Agent', { exact: true })).toBeVisible()
    await expect(page.getByText('Import Agent', { exact: true })).toBeVisible()
  })
})
