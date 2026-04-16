import type { Page } from '@playwright/test'
import { expect } from '@playwright/test'

export const ADMIN_LOGIN_PATH = '/admin/login'
export const ADMIN_APPLICATION_URL = /\/admin\/application(?:$|\?|\/)/
const ADMIN_LOGIN_URL = /\/admin\/login(?:$|\?|\/)/
const ADMIN_PASSWORD = 'TestPassword123!'

// Bilingual locator patterns (EN | zh-CN)
export const USERNAME_RE = /Please enter username|请输入用户名/
export const PASSWORD_RE = /Please enter password|请输入密码/
export const LOGIN_BTN_RE = /Login|登录/
export const NEW_PASSWORD_RE = /Please enter your new password|请输入(新|修改)密码/
export const SAVE_BTN_RE = /Save|保存/

async function waitForToken(page: Page) {
  await expect
    .poll(async () => {
      return page.evaluate(() => Boolean(localStorage.getItem('token')))
    }, { timeout: 30000 })
    .toBe(true)
}

async function getCurrentUserProfile(page: Page) {
  return page.evaluate(async () => {
    try {
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
    } catch {
      return null
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
  const dialog = page.locator('.el-dialog').filter({ hasText: /Change Password|修改密码/ })
  if (!(await dialog.isVisible().catch(() => false))) {
    return false
  }

  const passwordInputs = dialog.getByPlaceholder(NEW_PASSWORD_RE)
  await passwordInputs.nth(0).fill(ADMIN_PASSWORD)
  await passwordInputs.nth(1).fill(ADMIN_PASSWORD)
  await dialog.getByRole('button', { name: SAVE_BTN_RE }).click()
  await expect(page).toHaveURL(ADMIN_LOGIN_URL, { timeout: 10000 })
  return true
}

async function fillLoginForm(page: Page) {
  const usernameInput = page.getByPlaceholder(USERNAME_RE)
  const passwordInput = page.getByPlaceholder(PASSWORD_RE)

  await usernameInput.fill('admin')
  await passwordInput.fill(ADMIN_PASSWORD)
  await expect(usernameInput).toHaveValue('admin')
  await expect(passwordInput).toHaveValue(ADMIN_PASSWORD)
}

export async function gotoLogin(page: Page) {
  await page.goto(ADMIN_LOGIN_PATH)
  await expect(page).toHaveURL(ADMIN_LOGIN_URL)
  await expect(page.getByPlaceholder(USERNAME_RE)).toBeVisible({ timeout: 15000 })
  await expect(page.getByPlaceholder(PASSWORD_RE)).toBeVisible()
}

async function submitLoginAndWaitForToken(page: Page) {
  const loginBtn = page.getByRole('button', { name: LOGIN_BTN_RE })

  await expect(loginBtn).toBeEnabled()
  await expect(loginBtn).not.toHaveAttribute('aria-busy', 'true')

  // Give Element Plus form model time to sync input values internally
  await page.waitForTimeout(100)

  await loginBtn.click()

  try {
    await waitForToken(page)
  } catch (e) {
    const stillOnLogin = await page.getByPlaceholder(USERNAME_RE).isVisible().catch(() => false)
    if (stillOnLogin) {
      await page.waitForTimeout(1000)
      await fillLoginForm(page)
      await expect(loginBtn).toBeEnabled()
      await loginBtn.click()
      await waitForToken(page)
    } else {
      throw e
    }
  }
}

export async function loginAsAdmin(page: Page) {
  await gotoLogin(page)

  await fillLoginForm(page)
  await submitLoginAndWaitForToken(page)

  if (await clearRequiredPasswordChangeDialog(page)) {
    await fillLoginForm(page)
    await submitLoginAndWaitForToken(page)
  }

  if (await clearRequiredPasswordChange(page)) {
    await gotoLogin(page)
    await fillLoginForm(page)
    await submitLoginAndWaitForToken(page)
  }

  await expect(page).toHaveURL(ADMIN_APPLICATION_URL, { timeout: 15000 })
}
