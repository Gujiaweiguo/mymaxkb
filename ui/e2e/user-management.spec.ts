import { testWithCleanup as test, expect } from './fixtures'

import { loginAsAdmin } from './helpers/auth'
import { uniqueEmail, uniqueId, uniqueUsername } from './helpers/data'
import { exactText } from './helpers/i18n'

const USER_HEADING = exactText('User', '用户管理')
const CREATE_USER_BUTTON = exactText('Create User', '创建用户')
const SAVE_BUTTON = exactText('Save', '保存')
const USERNAME_PLACEHOLDER = exactText('Please enter username', '请输入用户名')
const NAME_PLACEHOLDER = exactText('Please enter name', '请输入姓名')
const EMAIL_PLACEHOLDER = exactText('Please enter email', '请输入邮箱')
const PHONE_PLACEHOLDER = exactText('Please enter phone', '请输入手机号')
const SEARCH_PLACEHOLDER = exactText('Please input', '请输入')
const EDIT_USER_TITLE = exactText('Edit User', '编辑用户')
const EDIT_TITLE = exactText('Edit', '编辑')
const DELETE_TITLE = exactText('Delete', '删除')
const DISABLED_STATUS = exactText('Disabled', '已禁用')
const CONFIRM_BUTTON = exactText('OK', '确定')

function buildPhoneNumber() {
  return `138${Date.now().toString().slice(-8)}`
}

async function trackCreatedUser(page, resourceTracker, username: string) {
  let userId: string | null = null

  await expect
    .poll(async () => {
      userId = await page.evaluate(async (targetUsername) => {
        const token = localStorage.getItem('token')
        if (!token) {
          return null
        }

        const response = await fetch(`/admin/api/user_manage/1/20?username=${encodeURIComponent(targetUsername)}`, {
          headers: {
            AUTHORIZATION: `Bearer ${token}`,
            'Accept-Language': 'en-US',
          },
        })

        const body = await response.json()
        return body?.data?.records?.find((item) => item.username === targetUsername)?.id ?? null
      }, username)
      return userId
    }, { timeout: 15000 })
    .toBeTruthy()

  resourceTracker.track({ type: 'user', id: userId!, name: username })
}

test.describe('@advisory User Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/system/user')
  })

  test('should navigate to the user management page', async ({ page }) => {
    await expect(page).toHaveURL(/\/admin\/system\/user(?:$|\?|\/)/)
    await expect(page.getByRole('heading', { name: USER_HEADING })).toBeVisible()
  })

  test('should display the user table and create control', async ({ page }) => {
    await expect(page.getByRole('button', { name: CREATE_USER_BUTTON })).toBeVisible()
    await expect(page.locator('.app-table')).toBeVisible()
  })

  test('should create, search, edit, disable, and delete a user', async ({ page, resourceTracker }) => {
    const username = uniqueUsername('e2euser')
    const email = uniqueEmail('e2euser')
    const createdName = `E2E User ${uniqueId('name')}`
    const updatedName = `${createdName} Updated`
    const phone = buildPhoneNumber()

    await page.getByRole('button', { name: CREATE_USER_BUTTON }).click()

    const drawer = page.locator('.el-drawer').filter({ has: page.getByRole('button', { name: SAVE_BUTTON }) })
    await expect(drawer).toBeVisible()
    await drawer.getByPlaceholder(USERNAME_PLACEHOLDER).fill(username)
    await drawer.getByPlaceholder(NAME_PLACEHOLDER).fill(createdName)
    await drawer.getByPlaceholder(EMAIL_PLACEHOLDER).fill(email)
    await drawer.getByPlaceholder(PHONE_PLACEHOLDER).fill(phone)
    await drawer.getByRole('button', { name: SAVE_BUTTON }).click()

    await trackCreatedUser(page, resourceTracker, username)
    await page.goto('/admin/system/user')
    await expect(page).toHaveURL(/\/admin\/system\/user(?:$|\?|\/)/)

    const searchInput = page.getByPlaceholder(SEARCH_PLACEHOLDER)
    await searchInput.fill(username)
    await searchInput.blur()

    const userRow = page.locator('tr', { hasText: username })
    await expect(userRow).toContainText(createdName)
    await expect(userRow).toContainText(email)

    await userRow.getByTitle(EDIT_TITLE).click()
    const editDrawer = page.locator('.el-drawer').filter({ has: page.getByText(EDIT_USER_TITLE) })
    await expect(editDrawer).toBeVisible()
    await editDrawer.getByPlaceholder(NAME_PLACEHOLDER).fill(updatedName)
    await editDrawer.getByRole('button', { name: SAVE_BUTTON }).click()
    await expect(editDrawer).toBeHidden()
    await expect(userRow).toContainText(updatedName)

    const statusSwitch = userRow.locator('.el-switch').first()
    await statusSwitch.click()
    await expect(userRow.getByText(DISABLED_STATUS)).toBeVisible()

    await userRow.getByTitle(DELETE_TITLE).click()
    const confirmDialog = page.locator('.el-message-box').last()
    await expect(confirmDialog).toBeVisible()
    await confirmDialog.getByRole('button', { name: CONFIRM_BUTTON }).click()

    await expect(userRow).toBeHidden()
    resourceTracker.clear()
  })
})
