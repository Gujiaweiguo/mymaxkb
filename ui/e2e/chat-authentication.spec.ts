import { testWithCleanup as test, expect } from './fixtures'
import { loginAsAdmin } from './helpers/auth'
import { exactText } from './helpers/i18n'

const AUTH_TITLE = exactText('Login Authentication', '登录认证')
const SCAN_TAB = exactText('Scan the QR code', '扫码登录')

test.describe('@advisory Chat Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/system/chat/authentication')
  })

  test('should navigate to the chat authentication page', async ({ page }) => {
    await expect(page).toHaveURL(/\/admin\/system\/chat\/authentication(?:$|\?|\/)/)
    await expect(page.getByText(AUTH_TITLE).first()).toBeVisible()
  })

  test('should display Scan QR Code tab in CE edition', async ({ page }) => {
    // CE edition shows only SCAN tab; EE has LDAP, CAS, OIDC, OAuth2, SCAN
    await expect(page.getByText(SCAN_TAB).first()).toBeVisible()
  })

  test('should display authentication page with h4 heading', async ({ page }) => {
    await expect(page.locator('h4').filter({ hasText: AUTH_TITLE })).toBeVisible()
  })
})
