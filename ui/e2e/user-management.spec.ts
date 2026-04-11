import { testWithCleanup as test, expect } from './fixtures'

import { loginAsAdmin } from './helpers/auth'
import { uniqueEmail, uniqueId, uniqueUsername } from './helpers/data'

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
    await expect(page.getByRole('heading', { name: 'User' })).toBeVisible()
  })

  test('should display the user table and create control', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'Create User' })).toBeVisible()
    await expect(page.locator('.app-table')).toBeVisible()
  })

  test('should create, search, edit, disable, and delete a user', async ({ page, resourceTracker }) => {
    const username = uniqueUsername('e2euser')
    const email = uniqueEmail('e2euser')
    const createdName = `E2E User ${uniqueId('name')}`
    const updatedName = `${createdName} Updated`
    const phone = buildPhoneNumber()

    await page.getByRole('button', { name: 'Create User' }).click()

    const drawer = page.locator('.el-drawer').filter({ has: page.getByRole('button', { name: 'Save' }) })
    await expect(drawer).toBeVisible()
    await drawer.getByPlaceholder('Please enter username').fill(username)
    await drawer.getByPlaceholder('Please enter name').fill(createdName)
    await drawer.getByPlaceholder('Please enter email').fill(email)
    await drawer.getByPlaceholder('Please enter phone').fill(phone)
    await drawer.getByRole('button', { name: 'Save' }).click()

    await trackCreatedUser(page, resourceTracker, username)
    await page.goto('/admin/system/user')
    await expect(page).toHaveURL(/\/admin\/system\/user(?:$|\?|\/)/)

    const searchInput = page.getByPlaceholder('Please input')
    await searchInput.fill(username)
    await searchInput.blur()

    const userRow = page.locator('tr', { hasText: username })
    await expect(userRow).toContainText(createdName)
    await expect(userRow).toContainText(email)

    await userRow.getByTitle('Edit').click()
    const editDrawer = page.locator('.el-drawer').filter({ has: page.getByText('Edit User') })
    await expect(editDrawer).toBeVisible()
    await editDrawer.getByPlaceholder('Please enter name').fill(updatedName)
    await editDrawer.getByRole('button', { name: 'Save' }).click()
    await expect(editDrawer).toBeHidden()
    await expect(userRow).toContainText(updatedName)

    const statusSwitch = userRow.locator('.el-switch').first()
    await statusSwitch.click()
    await expect(userRow).toContainText('Disabled')

    await userRow.getByTitle('Delete').click()
    const confirmDialog = page.locator('.el-message-box').last()
    await expect(confirmDialog).toBeVisible()
    await confirmDialog.getByRole('button', { name: 'OK' }).click()

    await expect(userRow).toBeHidden()
    resourceTracker.clear()
  })
})
