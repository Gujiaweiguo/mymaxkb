import { testWithCleanup as test, expect } from './fixtures'

import { loginAsAdmin } from './helpers/auth'
import { uniqueToolName } from './helpers/data'
import { exactText } from './helpers/i18n'

const TOOL_HEADING = exactText('Tool', '工具')
const SEARCH_PLACEHOLDER = exactText('Search by name', '按名称搜索')
const CREATE_BUTTON = exactText('Create', '创建')
const CREATE_TOOL_ITEM = exactText('Create Tool', '创建工具')
const DELETE_MENU_ITEM = exactText('Delete', '删除')
const CONFIRM_BUTTON = exactText('OK', '确定')

test.describe('@advisory Tool Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/tool')
  })

  test('should navigate to the tool page', async ({ page }) => {
    await expect(page).toHaveURL(/\/admin\/tool(?:$|\?|\/)/)
    await expect(page.locator('.tool-manage')).toBeVisible()
    await expect(page.locator('h4').filter({ hasText: TOOL_HEADING }).first()).toBeVisible()
  })

  test('should display filter controls and create button', async ({ page }) => {
    await expect(page.locator('.el-radio-button')).toHaveCount(6)
    await expect(page.getByPlaceholder(SEARCH_PLACEHOLDER)).toBeVisible()
    await expect(page.getByRole('button', { name: CREATE_BUTTON })).toBeVisible()
  })

  test('should open create tool dialog from dropdown', async ({ page }) => {
    await page.getByRole('button', { name: CREATE_BUTTON }).click()
    await page.getByRole('menuitem', { name: CREATE_TOOL_ITEM }).click()
    const drawer = page.locator('.el-drawer').filter({ hasText: TOOL_HEADING })
    await expect(drawer).toBeVisible()
    await expect(drawer.getByPlaceholder(exactText('Please enter the tool name', '请输入工具名称'))).toBeVisible()
    await drawer.getByRole('button', { name: exactText('Cancel', '取消') }).click()
    await expect(drawer).toBeHidden()
  })
})
