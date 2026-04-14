import type { Page } from '@playwright/test'
import { expect } from '@playwright/test'

export const ADMIN_LOGIN_PATH = '/admin/login'
export const ADMIN_APPLICATION_URL = /\/admin\/application(?:$|\?|\/)/
const ADMIN_LOGIN_URL = /\/admin\/login(?:$|\?|\/)/
const ADMIN_PASSWORD = 'TestPassword123!'

async function waitForToken(page: Page) {
  await expect
    .poll(async () => {
      return page.evaluate(() => Boolean(localStorage.getItem('token')))
    }, { timeout: 30000 })
    .toBe(true)
}

async function getCurrentUserProfile(page: Page) {
  return page.evaluate(async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      return null
    }

    const response = await fetch('/admin/api/user/profile', {
      headers: {
        AUTHORIZATION: `Bearer ${token}`,
        'Accept-Language': 'en-US',
      },
    })

    return {
      status: response.status,
      body: await response.json(),
    }
  })
}

async function clearRequiredPasswordChange(page: Page) {
  const profile = await getCurrentUserProfile(page)
  if (!profile || profile.status !== 200 || !profile.body?.data?.is_edit_password) {
    return false
  }

  const resetResult = await page.evaluate(async (password) => {
    const token = localStorage.getItem('token')
    if (!token) {
      return null
    }

    const response = await fetch('/admin/api/user/current/reset_password', {
      method: 'POST',
      headers: {
        AUTHORIZATION: `Bearer ${token}`,
        'Accept-Language': 'en-US',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        password,
        re_password: password,
      }),
    })

    const body = await response.json()
    localStorage.removeItem('token')

    return {
      status: response.status,
      body,
    }
  }, ADMIN_PASSWORD)

  expect(resetResult?.status).toBe(200)
  expect(resetResult?.body?.code).toBe(200)

  return true
}

async function clearRequiredPasswordChangeDialog(page: Page) {
  const dialog = page.locator('.el-dialog').filter({ hasText: 'Change Password' })
  if (!(await dialog.isVisible().catch(() => false))) {
    return false
  }

  const passwordInputs = dialog.getByPlaceholder('Please enter your new password')
  await passwordInputs.nth(0).fill(ADMIN_PASSWORD)
  await passwordInputs.nth(1).fill(ADMIN_PASSWORD)
  await dialog.getByRole('button', { name: 'Save' }).click()
  await expect(page).toHaveURL(ADMIN_LOGIN_URL, { timeout: 10000 })
  return true
}

async function fillLoginForm(page: Page) {
  const usernameInput = page.getByPlaceholder('Please enter username')
  const passwordInput = page.getByPlaceholder('Please enter password')

  await usernameInput.fill('admin')
  await passwordInput.fill(ADMIN_PASSWORD)
  await expect(usernameInput).toHaveValue('admin')
  await expect(passwordInput).toHaveValue(ADMIN_PASSWORD)
}

export async function gotoLogin(page: Page) {
  await Promise.all([
    page.waitForResponse((response) => response.url().includes('/admin/api/profile') && response.ok()),
    page.waitForResponse(
      (response) => response.url().includes('/admin/api/login/auth/setting') && response.ok(),
    ),
    page.goto(ADMIN_LOGIN_PATH),
  ])
  await page.waitForLoadState('networkidle')
  await expect(page).toHaveURL(ADMIN_LOGIN_URL)
  await expect(page.getByPlaceholder('Please enter username')).toBeVisible()
  await expect(page.getByPlaceholder('Please enter password')).toBeVisible()
}

export async function loginAsAdmin(page: Page) {
  await gotoLogin(page)

  await fillLoginForm(page)
  await page.getByRole('button', { name: 'Login' }).click()
  await waitForToken(page)

  if (await clearRequiredPasswordChangeDialog(page)) {
    await fillLoginForm(page)
    await page.getByRole('button', { name: 'Login' }).click()
    await waitForToken(page)
  }

  if (await clearRequiredPasswordChange(page)) {
    await gotoLogin(page)
    await fillLoginForm(page)
    await page.getByRole('button', { name: 'Login' }).click()
    await waitForToken(page)
  }

  await expect(page).toHaveURL(ADMIN_APPLICATION_URL, { timeout: 10000 })
}
