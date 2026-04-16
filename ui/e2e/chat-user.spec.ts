import { testWithCleanup as test, expect } from './fixtures'

import { loginAsAdmin } from './helpers/auth'
import { exactText } from './helpers/i18n'

const CHAT_USER_TITLE = exactText('Chat Users', '对话用户')
const CREATE_USER = exactText('Create User', '创建用户')
const USERNAME_COL = exactText('Username', '用户名')
const NAME_COL = exactText('Name', '姓名')
const STATUS_COL = exactText('Status', '状态')

test.describe('@advisory Chat User Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/system/chat/chat-user')
  })

  test('should navigate to the chat user page', async ({ page }) => {
    await expect(page).toHaveURL(/\/admin\/system\/chat\/chat-user(?:$|\?|\/)/)
    await expect(page.locator('.el-table')).toBeVisible()
  })

  test('should display action buttons and search controls', async ({ page }) => {
    await expect(page.getByRole('button', { name: CREATE_USER })).toBeVisible()
    await expect(page.locator('.el-select').first()).toBeVisible()
  })

  test('should display table column headers', async ({ page }) => {
    await expect(page.getByText(USERNAME_COL).first()).toBeVisible()
    await expect(page.getByText(NAME_COL).first()).toBeVisible()
    await expect(page.getByText(STATUS_COL).first()).toBeVisible()
  })
})
