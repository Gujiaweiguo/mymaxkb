import { test, expect } from '@playwright/test'

import {
  ADMIN_APPLICATION_URL,
  LOGIN_BTN_RE,
  NEW_PASSWORD_RE,
  PASSWORD_RE,
  SAVE_BTN_RE,
  USERNAME_RE,
  gotoLogin,
  loginAsAdmin,
} from './helpers/auth'

test.describe('@advisory Login Flow', () => {
  test.beforeEach(async ({ page }) => {
    await gotoLogin(page)
  })

  test('should display login form', async ({ page }) => {
    await expect(page).toHaveURL(/\/admin\/login(?:$|\?|\/)/)
    await expect(page.getByPlaceholder(USERNAME_RE)).toBeVisible()
    await expect(page.getByPlaceholder(PASSWORD_RE)).toBeVisible()
    await expect(page.getByRole('button', { name: LOGIN_BTN_RE })).toBeVisible()
  })

  test('should login with valid credentials', async ({ page }) => {
    await loginAsAdmin(page)
    await expect(page).toHaveURL(ADMIN_APPLICATION_URL)
  })

  test('form inputs retain values after fill — guards page readiness', async ({ page }) => {
    const usernameInput = page.getByPlaceholder(USERNAME_RE)
    const passwordInput = page.getByPlaceholder(PASSWORD_RE)

    await usernameInput.fill('admin')
    await passwordInput.fill('TestPassword123!')

    await expect(usernameInput).toHaveValue('admin')
    await expect(passwordInput).toHaveValue('TestPassword123!')
  })

  test('raw form submit persists auth token in localStorage', async ({ page }) => {
    await page.getByPlaceholder(USERNAME_RE).fill('admin')
    await page.getByPlaceholder(PASSWORD_RE).fill('TestPassword123!')

    await page.waitForTimeout(300)
    await page.getByRole('button', { name: LOGIN_BTN_RE }).click()

    await expect
      .poll(async () => page.evaluate(() => Boolean(localStorage.getItem('token'))), {
        timeout: 30000,
      })
      .toBe(true)

    await expect(page).toHaveURL(ADMIN_APPLICATION_URL, { timeout: 15000 })
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
            nick_name: username,
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
    await page.getByPlaceholder(USERNAME_RE).fill(username)
    await page.getByPlaceholder(PASSWORD_RE).fill(initialPassword)
    await page.getByRole('button', { name: LOGIN_BTN_RE }).click()

    await expect(page).toHaveURL(/\/admin\/force-password-change(?:$|\?|\/)/)

    const passwordInputs = page.getByPlaceholder(NEW_PASSWORD_RE)
    await passwordInputs.nth(0).fill(nextPassword)
    await passwordInputs.nth(1).fill(nextPassword)
    await page.getByRole('button', { name: SAVE_BTN_RE }).click()

    await expect(page).toHaveURL(/\/admin\/login(?:$|\?|\/)/)

    await page.getByPlaceholder(USERNAME_RE).fill(username)
    await page.getByPlaceholder(PASSWORD_RE).fill(nextPassword)
    await page.getByRole('button', { name: LOGIN_BTN_RE }).click()

    await expect(page).toHaveURL(ADMIN_APPLICATION_URL)
  })

  test('should show error with invalid credentials', async ({ page }) => {
    await page.getByPlaceholder(USERNAME_RE).fill('nonexistent_test_user')
    await page.getByPlaceholder(PASSWORD_RE).fill('WrongPassword123!')
    await page.getByRole('button', { name: LOGIN_BTN_RE }).click()

    await expect(page).toHaveURL(/\/admin\/login(?:$|\?|\/)/)
    await expect(page.getByPlaceholder(USERNAME_RE)).toBeVisible()
  })

  test('should show validation for empty fields', async ({ page }) => {
    await page.getByRole('button', { name: LOGIN_BTN_RE }).click()

    await expect(page.locator('.login-form .el-form-item__error')).toHaveCount(2)
  })
})
