import { testWithCleanup as test, expect } from './fixtures'
import { loginAsAdmin } from './helpers/auth'
import { exactText } from './helpers/i18n'

const EMAIL_TITLE = exactText('Email Settings', '邮箱设置')
const SMTP_HOST = exactText('SMTP Host', 'SMTP Host')
const SMTP_PORT = exactText('SMTP Port', 'SMTP Port')
const SAVE = exactText('Save', '保存')
const TEST_CONNECTION = exactText('Test Connection', '测试连接')

test.describe('@advisory Email Settings', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/system/email')
  })

  test('should navigate to the email settings page', async ({ page }) => {
    await expect(page).toHaveURL(/\/admin\/system\/email(?:$|\?|\/)/)
    await expect(page.getByText(EMAIL_TITLE).first()).toBeVisible()
  })

  test('should display SMTP form fields', async ({ page }) => {
    await expect(page.getByText(SMTP_HOST).first()).toBeVisible()
    await expect(page.getByText(SMTP_PORT).first()).toBeVisible()
  })

  test('should display Save and Test Connection buttons', async ({ page }) => {
    await expect(page.getByRole('button', { name: SAVE })).toBeVisible()
    await expect(page.getByRole('button', { name: TEST_CONNECTION })).toBeVisible()
  })
})
