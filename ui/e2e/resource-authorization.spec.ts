import { testWithCleanup as test, expect } from './fixtures'

import { loginAsAdmin } from './helpers/auth'
import { exactText } from './helpers/i18n'

const RESOURCE_AUTH = exactText('Resource Authorization', '资源授权')
const AGENT = exactText('Agent', '智能体')
const KNOWLEDGE = exactText('Knowledge', '知识库')
const MEMBER = exactText('Member', '成员')
const PERMISSION_SETTING = exactText('Permission Setting', '资源权限配置')

test.describe('@advisory Resource Authorization', () => {
  test('should navigate to the application authorization page', async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/system/authorization/application')
    await expect(page.locator('.el-loading-mask')).toHaveCount(0, { timeout: 30_000 })
    await expect(page).toHaveURL(/\/admin\/system\/authorization\/application(?:$|\?|\/)/)
    await expect(page.locator('.el-breadcrumb').getByText(RESOURCE_AUTH)).toBeVisible()
    await expect(page.locator('.el-breadcrumb').getByText(AGENT)).toBeVisible()
  })

  test('should display panel headings and search shell on application authorization', async ({
    page,
  }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/system/authorization/application')
    await expect(page.locator('.el-loading-mask')).toHaveCount(0, { timeout: 30_000 })
    await expect(page.getByText(MEMBER).first()).toBeVisible()
    await expect(page.getByText(PERMISSION_SETTING).first()).toBeVisible()
    await expect(page.locator('.el-input').first()).toBeVisible()
  })

  test('should change breadcrumb correctly when navigating to knowledge authorization', async ({
    page,
  }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/system/authorization/knowledge')
    await expect(page.locator('.el-loading-mask')).toHaveCount(0, { timeout: 30_000 })
    await expect(page).toHaveURL(/\/admin\/system\/authorization\/knowledge(?:$|\?|\/)/)
    await expect(page.locator('.el-breadcrumb').getByText(KNOWLEDGE)).toBeVisible()
    await expect(page.getByText(MEMBER).first()).toBeVisible()
  })
})
