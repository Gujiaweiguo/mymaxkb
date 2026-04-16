import { testWithCleanup as test, expect } from './fixtures'
import { loginAsAdmin } from './helpers/auth'
import { exactText } from './helpers/i18n'

const GROUP_TITLE = exactText('User Groups', '用户组')
const ADD_MEMBER = exactText('Add Member', '添加成员')
const USERNAME_COL = exactText('Username', '用户名')
const NAME_COL = exactText('Name', '姓名')

test.describe('@advisory User Groups', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/system/chat/group')
  })

  test('should navigate to the user groups page', async ({ page }) => {
    await expect(page).toHaveURL(/\/admin\/system\/chat\/group(?:$|\?|\/)/)
    await expect(page.getByText(GROUP_TITLE).first()).toBeVisible()
  })

  test('should display group list panel with search', async ({ page }) => {
    await expect(page.locator('.user-left').getByText(GROUP_TITLE).first()).toBeVisible()
    await expect(page.locator('.user-left').getByPlaceholder(/Search|搜索/)).toBeVisible()
  })

  test('should display member table and Add Member button in right panel', async ({ page }) => {
    await expect(page.locator('.el-table')).toBeVisible()
    await expect(page.getByRole('button', { name: ADD_MEMBER })).toBeVisible()
    await expect(page.getByText(USERNAME_COL).first()).toBeVisible()
    await expect(page.getByText(NAME_COL).first()).toBeVisible()
  })
})
