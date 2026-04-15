import { request } from '@playwright/test'

const ADMIN_PASSWORD = 'TestPassword123!'
const MAX_LOGIN_ATTEMPTS = 3

async function sleep(ms: number) {
  await new Promise((resolve) => setTimeout(resolve, ms))
}

/**
 * Global setup runs once before all tests.
 * Clears the admin's forced-password-change flag so tests don't
 * waste time on the password-reset dance during loginAsAdmin.
 */
async function globalSetup() {
  const baseURL = process.env.E2E_BASE_URL || 'http://localhost:3000'
  const apiContext = await request.newContext({ baseURL })

  let loginResponse = null

  for (let attempt = 1; attempt <= MAX_LOGIN_ATTEMPTS; attempt += 1) {
    loginResponse = await apiContext.post('/admin/api/user/login', {
      form: {
        username: 'admin',
        password: ADMIN_PASSWORD,
      },
    })

    if (loginResponse.ok()) {
      break
    }

    if (attempt < MAX_LOGIN_ATTEMPTS) {
      console.warn(`[global-setup] Admin login attempt ${attempt} failed, retrying`)
      await sleep(5000)
    }
  }

  if (!loginResponse?.ok()) {
    await apiContext.dispose()
    throw new Error('[global-setup] Admin login failed after retries')
  }

  const loginBody = await loginResponse.json()
  const token = loginBody?.data?.token
  if (!token) {
    await apiContext.dispose()
    throw new Error('[global-setup] No token in login response')
  }

  // Check if password change is required
  const profileResponse = await apiContext.get('/admin/api/user/profile', {
    headers: { AUTHORIZATION: `Bearer ${token}` },
  })
  const profileBody = await profileResponse.json()
  const needsPasswordChange = profileBody?.data?.is_edit_password === true

  if (!needsPasswordChange) {
    await apiContext.dispose()
    return
  }

  // Reset password to the same value to clear the flag
  const resetResponse = await apiContext.post('/admin/api/user/current/reset_password', {
    headers: {
      AUTHORIZATION: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    data: {
      password: ADMIN_PASSWORD,
      re_password: ADMIN_PASSWORD,
    },
  })

  if (resetResponse.ok()) {
    console.log('[global-setup] Admin password-change flag cleared')
  } else {
    await apiContext.dispose()
    throw new Error('[global-setup] Failed to clear password-change flag')
  }

  await apiContext.dispose()
}

export default globalSetup
