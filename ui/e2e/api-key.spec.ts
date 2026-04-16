import { testWithCleanup as test, expect } from './fixtures'
import { loginAsAdmin } from './helpers/auth'
import { exactText } from './helpers/i18n'

const API_KEY_TITLE = /API Key/i
const CREATE = exactText('Create', '创建')
const ACTION = exactText('Action', '操作')
const EXPIRATION = exactText('Expiration Date', '到期时间')

test.describe('@advisory API Key Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/system/api-key')
  })

  test('should navigate to the API key page', async ({ page }) => {
    await expect(page).toHaveURL(/\/admin\/system\/api-key(?:$|\?|\/)/)
    await expect(page.getByText(API_KEY_TITLE).first()).toBeVisible()
  })

  test('should display Create button', async ({ page }) => {
    await expect(page.getByRole('button', { name: CREATE })).toBeVisible()
  })

  test('should display table with expected columns', async ({ page }) => {
    await expect(page.locator('.el-table')).toBeVisible()
    await expect(page.getByText(EXPIRATION).first()).toBeVisible()
    await expect(page.getByText(ACTION).first()).toBeVisible()
  })
})
