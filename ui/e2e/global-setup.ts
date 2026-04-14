import { request } from '@playwright/test'

/**
 * Global setup runs once before all tests.
 * Clears the admin's forced-password-change flag so tests don't
 * waste time on the password-reset dance during loginAsAdmin.
 */
async function globalSetup() {
  const baseURL = process.env.E2E_BASE_URL || 'http://localhost:3000'
  const apiContext = await request.newContext({ baseURL })

  // Login as admin
  const loginResponse = await apiContext.post('/admin/api/user/login', {
    form: {
      username: 'admin',
      password: 'TestPassword123!',
    },
  })

  if (!loginResponse.ok()) {
    console.warn('[global-setup] Admin login failed — skipping password flag clear')
    await apiContext.dispose()
    return
  }

  const loginBody = await loginResponse.json()
  const token = loginBody?.data?.token
  if (!token) {
    console.warn('[global-setup] No token in login response — skipping')
    await apiContext.dispose()
    return
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
      password: 'TestPassword123!',
      re_password: 'TestPassword123!',
    },
  })

  if (resetResponse.ok()) {
    console.log('[global-setup] Admin password-change flag cleared')
  } else {
    console.warn('[global-setup] Failed to clear password-change flag')
  }

  await apiContext.dispose()
}

export default globalSetup
