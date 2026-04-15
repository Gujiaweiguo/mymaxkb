import { testWithCleanup as test, expect } from './fixtures'

import { loginAsAdmin } from './helpers/auth'
import { exactText } from './helpers/i18n'

const TRIGGER_HEADING = exactText('Trigger', '触发器')
const CREATE_BUTTON = exactText('Create', '创建')
const CREATE_TRIGGER = exactText('Create Trigger', '创建触发器')

test.describe('@advisory Trigger Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/trigger')
  })

  test('should navigate to the trigger page', async ({ page }) => {
    await expect(page).toHaveURL(/\/admin\/trigger(?:$|\?|\/)/)
    await expect(page.locator('h2').filter({ hasText: TRIGGER_HEADING })).toBeVisible()
    await expect(page.locator('.el-table')).toBeVisible()
  })

  test('should display action buttons and search controls', async ({ page }) => {
    await expect(page.getByRole('button', { name: CREATE_BUTTON })).toBeVisible()
    await expect(page.locator('.el-select').first()).toBeVisible()
  })

  test('should open Create Trigger drawer', async ({ page }) => {
    await page.getByRole('button', { name: CREATE_BUTTON }).click()
    // Use el-drawer__header to avoid strict-mode matches on hidden drawers
    await expect(page.locator('.el-drawer__header').filter({ hasText: CREATE_TRIGGER })).toBeVisible()
    await expect(page.locator('.el-drawer__body').last()).toBeVisible()
  })
})
