import { testWithCleanup as test, expect } from './fixtures'

import { loginAsAdmin } from './helpers/auth'
import { exactText } from './helpers/i18n'

const SHARED_RESOURCES = exactText('Shared Resources', '共享资源')
const TOOL = exactText('Tool', '工具')
const MODEL = exactText('Model', '模型')
const ALL_MODELS = exactText('All Models', '全部模型')

test.describe('@advisory Shared Resources', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
  })

  test('should display shared knowledge page', async ({ page }) => {
    await page.goto('/admin/system/shared/knowledge')
    await expect(page.locator('.el-loading-mask')).toHaveCount(0, { timeout: 30_000 })

    await expect(page).toHaveURL(/\/admin\/system\/shared\/knowledge(?:$|\?|\/)/)
    await expect(page.locator('.el-breadcrumb').getByText(SHARED_RESOURCES).first()).toBeVisible()
    await expect(page.locator('.complex-search__left')).toBeVisible()
  })

  test('should display shared tool page', async ({ page }) => {
    await page.goto('/admin/system/shared/tool')
    await expect(page.locator('.el-loading-mask')).toHaveCount(0, { timeout: 30_000 })

    await expect(page).toHaveURL(/\/admin\/system\/shared\/tool(?:$|\?|\/)/)
    await expect(page.locator('.el-breadcrumb').getByText(SHARED_RESOURCES).first()).toBeVisible()
    await expect(page.locator('.complex-search__left')).toBeVisible()
    await expect(page.getByText(TOOL).first()).toBeVisible()
    await expect(page.getByText('Skills').first()).toBeVisible()
    await expect(page.getByText('MCP').first()).toBeVisible()
  })

  test('should display shared model page', async ({ page }) => {
    await page.goto('/admin/system/shared/model')
    await expect(page.locator('.el-loading-mask')).toHaveCount(0, { timeout: 30_000 })

    await expect(page).toHaveURL(/\/admin\/system\/shared\/model(?:$|\?|\/)/)
    await expect(page.locator('.el-breadcrumb').getByText(SHARED_RESOURCES).first()).toBeVisible()
    await expect(page.locator('.el-breadcrumb').getByText(MODEL).first()).toBeVisible()
    await expect(page.locator('.shared-model-manage')).toBeVisible()
    await expect(page.getByText(ALL_MODELS).first()).toBeVisible()
  })
})
