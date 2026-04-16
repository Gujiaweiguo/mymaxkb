import { testWithCleanup as test, expect } from './fixtures'

import { loginAsAdmin } from './helpers/auth'
import { exactText } from './helpers/i18n'

const APPEARANCE_SETTINGS = exactText('Appearance Settings', '外观设置')
const PLATFORM_THEME = exactText('Platform Display Theme', '平台显示主题')
const DEFAULT_THEME = exactText('Default', '默认')
const SAVE_APPLY = exactText('Save and Apply', '保存并应用')
const RESTORE_DEFAULTS = exactText('Restore Defaults', '恢复默认')

test.describe('@advisory Theme Settings', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/system/setting/theme')
  })

  test('should navigate to the theme settings page', async ({ page }) => {
    await expect(page).toHaveURL(/\/admin\/system\/setting\/theme(?:$|\?|\/)/)
    await expect(page.getByText(APPEARANCE_SETTINGS).first()).toBeVisible()
  })

  test('should display theme options and platform login settings', async ({ page }) => {
    await expect(page.getByText(PLATFORM_THEME).first()).toBeVisible()
    await expect(page.getByText(DEFAULT_THEME).first()).toBeVisible()
    await expect(page.getByText(RESTORE_DEFAULTS).first()).toBeVisible()
  })

  test('should display Save and Apply button', async ({ page }) => {
    await expect(page.getByRole('button', { name: SAVE_APPLY })).toBeVisible()
  })
})
