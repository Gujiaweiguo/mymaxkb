import { test, expect } from '@playwright/test'

import { ADMIN_APPLICATION_URL, gotoLogin, loginAsAdmin } from './helpers/auth'

test.describe('@advisory Login Flow', () => {
  test.beforeEach(async ({ page }) => {
    await gotoLogin(page)
  })

  test('should display login form', async ({ page }) => {
    await expect(page).toHaveURL(/\/admin\/login(?:$|\?|\/)/)
    await expect(page.getByPlaceholder('Please enter username')).toBeVisible()
    await expect(page.getByPlaceholder('Please enter password')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Login' })).toBeVisible()
  })

  test('should login with valid credentials', async ({ page }) => {
    await loginAsAdmin(page)
    await expect(page).toHaveURL(ADMIN_APPLICATION_URL)
  })

  test('should show error with invalid credentials', async ({ page }) => {
    await page.getByPlaceholder('Please enter username').fill('admin')
    await page.getByPlaceholder('Please enter password').fill('WrongPassword')
    await page.getByRole('button', { name: 'Login' }).click()

    await expect(page).toHaveURL(/\/admin\/login(?:$|\?|\/)/)
    await expect(page.getByPlaceholder('Please enter username')).toBeVisible()
  })

  test('should show validation for empty fields', async ({ page }) => {
    await page.getByRole('button', { name: 'Login' }).click()

    await expect(page.locator('.login-form .el-form-item__error')).toHaveCount(2)
  })
})
