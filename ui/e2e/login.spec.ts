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

  test('should force a newly created local user to change password on first login', async ({ page }) => {
    await loginAsAdmin(page)

    const seed = Date.now()
    const username = `pw-change-${seed}`
    const initialPassword = 'TempPass123!'
    const nextPassword = 'NextPass123!'

    const createUserResult = await page.evaluate(
      async ({ username, initialPassword }) => {
        const token = localStorage.getItem('token')
        if (!token) {
          return null
        }

        const response = await fetch('/admin/api/user_manage', {
          method: 'POST',
          headers: {
            AUTHORIZATION: `Bearer ${token}`,
            'Accept-Language': 'en-US',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username,
            password: initialPassword,
            email: `${username}@example.com`,
            role: 'USER',
          }),
        })

        return {
          status: response.status,
          body: await response.json(),
        }
      },
      { username, initialPassword },
    )

    expect(createUserResult?.status).toBe(200)
    expect(createUserResult?.body?.code).toBe(200)

    await page.evaluate(() => {
      localStorage.removeItem('token')
    })

    await gotoLogin(page)
    await page.getByPlaceholder('Please enter username').fill(username)
    await page.getByPlaceholder('Please enter password').fill(initialPassword)
    await page.getByRole('button', { name: 'Login' }).click()

    await expect(page).toHaveURL(/\/admin\/force-password-change(?:$|\?|\/)/)

    const passwordInputs = page.getByPlaceholder('Please enter your new password')
    await passwordInputs.nth(0).fill(nextPassword)
    await passwordInputs.nth(1).fill(nextPassword)
    await page.getByRole('button', { name: 'Save' }).click()

    await expect(page).toHaveURL(/\/admin\/login(?:$|\?|\/)/)

    await page.getByPlaceholder('Please enter username').fill(username)
    await page.getByPlaceholder('Please enter password').fill(nextPassword)
    await page.getByRole('button', { name: 'Login' }).click()

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
