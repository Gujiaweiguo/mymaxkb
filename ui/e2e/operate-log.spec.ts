import { testWithCleanup as test, expect } from './fixtures'

import { loginAsAdmin } from './helpers/auth'
import { exactText } from './helpers/i18n'

const OPERATE_LOG_TITLE = exactText('Operate Logs', '操作日志')
const OPERATE_USER = exactText('Operate User', '操作用户')
const OPERATE_MENU = exactText('Operate Menu', '操作菜单')
const STATUS = exactText('Status', '状态')
const EXPORT = exactText('Export', '导出')

test.describe('@advisory Operation Log', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/operate')
  })

  test('should navigate to the operation log page', async ({ page }) => {
    await expect(page).toHaveURL(/\/admin\/operate(?:$|\?|\/)/)
    await expect(page.locator('h2').filter({ hasText: OPERATE_LOG_TITLE })).toBeVisible()
    await expect(page.locator('.el-table')).toBeVisible()
  })

  test('should display filter and export controls', async ({ page }) => {
    // Time range dropdown (default: "Last 7 Days")
    await expect(page.locator('.el-select').first()).toBeVisible()
    // Export button (admin has OPERATION_LOG_EXPORT)
    await expect(page.getByRole('button', { name: EXPORT })).toBeVisible()
  })

  test('should display table column headers', async ({ page }) => {
    await expect(page.getByText(OPERATE_MENU).first()).toBeVisible()
    await expect(page.getByText(OPERATE_USER).first()).toBeVisible()
    await expect(page.getByText(STATUS).first()).toBeVisible()
  })
})
