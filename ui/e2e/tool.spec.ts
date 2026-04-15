import { testWithCleanup as test, expect } from './fixtures'

import { loginAsAdmin } from './helpers/auth'
import { uniqueToolName } from './helpers/data'
import { exactText } from './helpers/i18n'

const TOOL_HEADING = exactText('Tool', '工具')
const SEARCH_PLACEHOLDER = exactText('Search by name', '按名称搜索')
const CREATE_BUTTON = exactText('Create', '创建')
const CREATE_TOOL_ITEM = exactText('Create Tool', '创建工具')
const TOOL_NAME_PLACEHOLDER = exactText('Please enter the tool name', '请输入工具名称')
const DELETE_MENU_ITEM = exactText('Delete', '删除')
const CONFIRM_BUTTON = exactText('OK', '确定')

async function createToolViaApi(page: import('@playwright/test').Page, toolName: string): Promise<string | null> {
  const toolId = await page.evaluate(async (name) => {
    const token = localStorage.getItem('token')
    const workspaceId = localStorage.getItem('workspace_id') || 'default'
    if (!token) {
      console.error('createToolViaApi: no token in localStorage')
      return null
    }

    try {
      const response = await fetch(`/admin/api/workspace/${workspaceId}/tool`, {
        method: 'POST',
        headers: {
          AUTHORIZATION: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name,
          code: 'def main():\n    return {"result": "e2e test"}',
        }),
      })

      const body = await response.json()
      if (!response.ok) {
        console.error('createToolViaApi: API error', response.status, JSON.stringify(body))
        return null
      }

      return body?.data?.id ?? null
    } catch (err) {
      console.error('createToolViaApi: fetch error', err)
      return null
    }
  }, toolName)

  return toolId
}

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

  test('should create a custom tool via API and verify it appears', async ({ page, resourceTracker }) => {
    const toolName = uniqueToolName()
    const toolId = await createToolViaApi(page, toolName)

    expect(toolId).toBeTruthy()
    resourceTracker.track({ type: 'tool', id: toolId!, name: toolName })

    await page.reload()
    await expect(page).toHaveURL(/\/admin\/tool(?:$|\?|\/)/)

    await page.getByPlaceholder(SEARCH_PLACEHOLDER).fill(toolName)
    await expect(page.getByText(toolName).first()).toBeVisible()
  })

  test('should delete a tool', async ({ page, resourceTracker }) => {
    const toolName = uniqueToolName()
    const toolId = await createToolViaApi(page, toolName)

    expect(toolId).toBeTruthy()
    resourceTracker.track({ type: 'tool', id: toolId!, name: toolName })

    await page.reload()
    await expect(page).toHaveURL(/\/admin\/tool(?:$|\?|\/)/)

    await page.getByPlaceholder(SEARCH_PLACEHOLDER).fill(toolName)
    const toolCard = page.locator('.card-box').filter({ hasText: toolName }).first()
    await expect(toolCard).toBeVisible()

    await toolCard.hover()
    const dropdownTrigger = toolCard.locator('.el-dropdown').getByRole('button')
    await dropdownTrigger.click()
    await page.getByRole('menuitem', { name: DELETE_MENU_ITEM }).last().click()

    const confirmDialog = page.locator('.el-message-box').last()
    await expect(confirmDialog).toBeVisible()
    await confirmDialog.getByRole('button', { name: CONFIRM_BUTTON }).click()

    await expect(page.locator('.card-box').filter({ hasText: toolName })).toHaveCount(0)
    resourceTracker.clear()
  })
})
