import { testWithCleanup as test, expect } from './fixtures'

import { loginAsAdmin } from './helpers/auth'
import { exactText } from './helpers/i18n'

const RESOURCE_MANAGEMENT = exactText('Resource Management', '资源管理')
const AGENT = exactText('Agent', '智能体')
const NAME = exactText('Name', '名称')
const CREATOR = exactText('Creator', '创建者')

const PAGE_URL = '/admin/system/resource-management/application'

test.describe('@advisory Resource Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto(PAGE_URL)
  })

  test('should navigate to the resource management page', async ({ page }) => {
    await expect(page).toHaveURL(/\/admin\/system\/resource-management\/application(?:$|\?|\/)/)
    await expect(page.locator('.el-loading-mask')).toHaveCount(0, { timeout: 30_000 })
    await expect(page.locator('.el-breadcrumb').getByText(RESOURCE_MANAGEMENT)).toBeVisible()
    await expect(page.locator('.el-breadcrumb').getByText(AGENT)).toBeVisible()
  })

  test('should display search controls and table shell', async ({ page }) => {
    await expect(page.locator('.complex-search__left')).toBeVisible()
    await expect(page.locator('.el-table')).toBeVisible()
    await expect(page.getByText(NAME).first()).toBeVisible()
    await expect(page.getByText(CREATOR).first()).toBeVisible()
  })

  test('should display pagination shell', async ({ page }) => {
    await expect(page.locator('.el-pagination')).toBeVisible()
  })
})
