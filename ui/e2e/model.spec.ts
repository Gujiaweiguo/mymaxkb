import { testWithCleanup as test, expect } from './fixtures'

import { loginAsAdmin } from './helpers/auth'
import { exactText } from './helpers/i18n'

const ALL_MODELS = exactText('All Models', '全部模型')
const PUBLIC_MODELS = exactText('Public Models', '公有模型')
const PRIVATE_MODELS = exactText('Private Models', '私有模型')
const ADD_MODEL = exactText('Add Model', '添加模型')
const SELECT_PROVIDER_TITLE = exactText('Select Provider', '选择供应商')

test.describe('@advisory Model Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/model')
  })

  test('should navigate to the model page', async ({ page }) => {
    await expect(page).toHaveURL(/\/admin\/model(?:$|\?|\/)/)
    await expect(page.locator('.layout-container')).toBeVisible()
  })

  test('should display provider sidebar sections', async ({ page }) => {
    await expect(page.getByText(ALL_MODELS).first()).toBeVisible()
    await expect(page.getByText(PUBLIC_MODELS).first()).toBeVisible()
    await expect(page.getByText(PRIVATE_MODELS).first()).toBeVisible()
  })

  test('should open Select Provider dialog when Add Model clicked', async ({ page }) => {
    await page.getByRole('button', { name: ADD_MODEL }).click()
    const dialog = page.locator('.el-dialog').filter({ hasText: SELECT_PROVIDER_TITLE })
    await expect(dialog).toBeVisible()
  })
})
