import { testWithCleanup as test, expect } from './fixtures'
import { loginAsAdmin } from './helpers/auth'
import { exactText } from './helpers/i18n'

const AUTH_TITLE = exactText('Login Authentication', '登录认证')
const LOGIN_SETTING = exactText('Login Setting', '登录设置')
const LOGIN_METHOD = exactText('Login Method', '登录方式')
const SAVE = exactText('Save', '保存')

test.describe('@advisory Authentication Settings', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/system/authentication')
  })

  test('should navigate to the authentication page', async ({ page }) => {
    await expect(page).toHaveURL(/\/admin\/system\/authentication(?:$|\?|\/)/)
    await expect(page.getByText(AUTH_TITLE).first()).toBeVisible()
  })

  test('should display Login Setting tab in CE', async ({ page }) => {
    // CE edition only shows "Login Setting" tab
    await expect(page.getByText(LOGIN_SETTING).first()).toBeVisible()
  })

  test('should display Login Method form and Save button', async ({ page }) => {
    // Wait for loading to complete (form fetches login methods from API)
    await expect(page.locator('.el-loading-mask')).toHaveCount(0, { timeout: 30000 })
    await expect(page.getByText(LOGIN_METHOD).first()).toBeVisible()
    await expect(page.getByRole('button', { name: SAVE })).toBeVisible()
  })
})
