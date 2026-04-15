import { testWithCleanup as test, expect } from './fixtures'
import { loginAsAdmin } from './helpers/auth'
import { exactText } from './helpers/i18n'

// Bilingual selectors
const INTERNAL_ROLE = exactText('System built-in roles', '系统内置角色')
const CUSTOM_ROLE = exactText('Custom roles', '自定义角色')
const PERMISSION_TAB = exactText('Permission configuration', '权限配置')
const MEMBER_TAB = exactText('Members', '成员')
const SYSTEM_ADMIN = exactText('System admin', '系统管理员')
const MODULE_NAME = exactText('Module name', '模块名称')

test.describe('@advisory Role Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/system/role')
  })

  test('should navigate to the role page and display role list', async ({ page }) => {
    await expect(page).toHaveURL(/\/admin\/system\/role(?:$|\?|\/)/)
    // Verify the left panel has "System built-in roles" section
    await expect(page.getByText(INTERNAL_ROLE).first()).toBeVisible()
    // Verify "Custom roles" section exists (may be empty in CE)
    await expect(page.getByText(CUSTOM_ROLE).first()).toBeVisible()
  })

  test('should display permission configuration tab for selected role', async ({ page }) => {
    // Permission configuration is the default active tab
    // Wait for initial page loading to complete (el-loading-mask blocks interaction)
    await expect(page.locator('.el-loading-mask')).toHaveCount(0, { timeout: 30000 })
    // Verify the permission table has "Module name" header
    await expect(page.getByText(MODULE_NAME).first()).toBeVisible()
  })

  test('should switch to Members tab', async ({ page }) => {
    // Wait for initial page loading to complete
    await expect(page.locator('.el-loading-mask')).toHaveCount(0, { timeout: 30000 })
    await page.locator('.el-radio-button__inner').filter({ hasText: MEMBER_TAB }).click()
    // Wait for member data to load and table to appear
    await expect(page.locator('.el-table')).toBeVisible({ timeout: 15000 })
  })
})
