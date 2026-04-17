import { type Page } from '@playwright/test'

import { testWithCleanup as test, expect } from './fixtures'

import { ADMIN_APPLICATION_URL, loginAsAdmin } from './helpers/auth'
import { uniqueApplicationName, type ResourceTracker } from './helpers/data'
import { exactText } from './helpers/i18n'

const APPLICATION_HEADING = exactText('Agent', '智能体')
const CREATE_BUTTON = exactText('Create', '创建')
const SIMPLE_AGENT_OPTION = exactText('Simple Agent', '简易智能体')
const ADVANCED_AGENT_OPTION = exactText('Advanced Agent', '高级智能体')
const IMPORT_AGENT_OPTION = exactText('Import Agent', '导入智能体')
const SETTING_HEADING = exactText('Settings', '设置')
const AGENT_NAME_PLACEHOLDER = exactText('Please enter the agent name', '请输入智能体名称')
const AGENT_DESCRIPTION_PLACEHOLDER = exactText(
  'Describe the Agent scenario and use, e.g.: XXX assistant answering user questions about XXX product usage',
  '描述该智能体的应用场景及用途，如：XXX 小助手回答用户提出的 XXX 产品使用问题',
)
const SEARCH_BY_NAME_PLACEHOLDER = exactText('Search by name', '按名称搜索')
const SAVE_BUTTON = exactText('Save', '保存')
const OVERVIEW_HEADING = exactText('Overview', '概览')
const ACCESS_HEADING = exactText('Third-Party Access', '接入第三方')

async function trackCreatedApplication(page: Page, resourceTracker: ResourceTracker, applicationName: string) {
  let applicationId: string | null = null

  await expect
    .poll(async () => {
      applicationId = await page.evaluate(async (targetName) => {
        const token = localStorage.getItem('token')
        const workspaceId = localStorage.getItem('workspace_id') || 'default'
        if (!token) {
          return null
        }

        const response = await fetch(
          `/admin/api/workspace/${workspaceId}/application/1/30?folder_id=default&name=${encodeURIComponent(targetName)}`,
          {
            headers: {
              AUTHORIZATION: `Bearer ${token}`,
              'Accept-Language': 'en-US',
            },
          },
        )

        const body = await response.json()
        return body?.data?.records?.find((item: { name: string }) => item.name === targetName)?.id ?? null
      }, applicationName)

      return applicationId
    }, { timeout: 15000 })
    .toBeTruthy()

  resourceTracker.track({ type: 'application', id: applicationId!, name: applicationName })
  return applicationId!
}

async function createSimpleApplication(page: Page, resourceTracker: ResourceTracker) {
  const applicationName = uniqueApplicationName()

  await page.getByRole('button', { name: CREATE_BUTTON }).click()
  await page.getByText(SIMPLE_AGENT_OPTION).click()

  const createDialog = page.locator('.el-dialog').filter({ has: page.getByRole('button', { name: CREATE_BUTTON }) })
  await expect(createDialog).toBeVisible()
  await createDialog.getByPlaceholder(AGENT_NAME_PLACEHOLDER).fill(applicationName)
  await createDialog.getByPlaceholder(AGENT_DESCRIPTION_PLACEHOLDER).fill('E2E detail page test')
  await createDialog.getByRole('button', { name: CREATE_BUTTON }).click()

  const applicationId = await trackCreatedApplication(page, resourceTracker, applicationName)
  await expect(page).toHaveURL(/\/application\/workspace\/[^/]+\/SIMPLE\/setting(?:$|\?|\/)/)

  return { applicationId, applicationName }
}

test.describe('@advisory Application Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
  })

  test('should land on the application page after login', async ({ page }) => {
    await expect(page).toHaveURL(ADMIN_APPLICATION_URL)
    await expect(page.locator('.application-manage')).toBeVisible()
    await expect(page.getByRole('heading', { name: APPLICATION_HEADING })).toBeVisible()
  })

  test('should display application search and create controls', async ({ page }) => {
    await expect(page.locator('.application-manage .complex-search')).toBeVisible()
    await expect(page.getByRole('button', { name: CREATE_BUTTON })).toBeVisible()
  })

  test('should open the create application menu', async ({ page }) => {
    await page.getByRole('button', { name: CREATE_BUTTON }).click()

    await expect(page.getByText(SIMPLE_AGENT_OPTION)).toBeVisible()
    await expect(page.getByText(ADVANCED_AGENT_OPTION)).toBeVisible()
    await expect(page.getByText(IMPORT_AGENT_OPTION)).toBeVisible()
  })

  test('should create an application and save configuration changes', async ({ page, resourceTracker }) => {
    const applicationName = uniqueApplicationName()
    const updatedDescription = `${applicationName} description updated in E2E`

    await page.getByRole('button', { name: CREATE_BUTTON }).click()
    await page.getByText(SIMPLE_AGENT_OPTION).click()

    const createDialog = page.locator('.el-dialog').filter({ has: page.getByRole('button', { name: CREATE_BUTTON }) })
    await expect(createDialog).toBeVisible()
    await createDialog.getByPlaceholder(AGENT_NAME_PLACEHOLDER).fill(applicationName)
    await createDialog.getByPlaceholder(AGENT_DESCRIPTION_PLACEHOLDER).fill('E2E application configuration flow')
    await createDialog.getByRole('button', { name: CREATE_BUTTON }).click()

    const applicationId = await trackCreatedApplication(page, resourceTracker, applicationName)
    await expect(page).toHaveURL(/\/application\/workspace\/[^/]+\/SIMPLE\/setting(?:$|\?|\/)/)
    await expect(page.locator('.application-setting')).toBeVisible()
    await expect(page.getByRole('heading', { name: SETTING_HEADING })).toBeVisible()
    await expect(page.getByPlaceholder(AGENT_NAME_PLACEHOLDER)).toHaveValue(applicationName)

    const descriptionInput = page.getByPlaceholder(AGENT_DESCRIPTION_PLACEHOLDER)
    await descriptionInput.fill(updatedDescription)
    await page.getByRole('button', { name: SAVE_BUTTON }).click()

    await page.goto('/admin/application')
    await expect(page).toHaveURL(ADMIN_APPLICATION_URL)

    const searchInput = page.getByPlaceholder(SEARCH_BY_NAME_PLACEHOLDER)
    await searchInput.fill(applicationName)
    await searchInput.blur()

    const applicationCard = page.locator('.application-manage').getByText(applicationName, { exact: true }).first()
    await expect(applicationCard).toBeVisible()

    await expect
      .poll(async () => {
        return page.evaluate(async (id) => {
          const token = localStorage.getItem('token')
          const workspaceId = localStorage.getItem('workspace_id') || 'default'
          if (!token) {
            return null
          }

          const response = await fetch(`/admin/api/workspace/${workspaceId}/application/${id}`, {
            headers: {
              AUTHORIZATION: `Bearer ${token}`,
              'Accept-Language': 'en-US',
            },
          })

          const body = await response.json()
          return body?.data?.desc ?? null
        }, applicationId)
      }, { timeout: 10000 })
      .toBe(updatedDescription)
  })

  test('should load the overview page for a created application', async ({ page, resourceTracker }) => {
    const { applicationId, applicationName } = await createSimpleApplication(page, resourceTracker)

    await page.goto(`/admin/application/workspace/${applicationId}/SIMPLE/overview`)
    await expect(page).toHaveURL(new RegExp(`/application/workspace/${applicationId}/SIMPLE/overview`))
    await expect(page.getByRole('heading', { name: OVERVIEW_HEADING })).toBeVisible()
    await expect(page.getByRole('heading', { name: applicationName, exact: true })).toBeVisible()
  })

  test('should load the setting page for a created application', async ({ page, resourceTracker }) => {
    const { applicationId, applicationName } = await createSimpleApplication(page, resourceTracker)

    await page.goto(`/admin/application/workspace/${applicationId}/SIMPLE/setting`)
    await expect(page).toHaveURL(new RegExp(`/application/workspace/${applicationId}/SIMPLE/setting`))
    await expect(page.locator('.application-setting')).toBeVisible()
    await expect(page.getByRole('heading', { name: SETTING_HEADING })).toBeVisible()
    await expect(page.getByPlaceholder(AGENT_NAME_PLACEHOLDER)).toHaveValue(applicationName)
  })

  test('should load the access page for a created application', async ({ page, resourceTracker }) => {
    const { applicationId } = await createSimpleApplication(page, resourceTracker)

    await page.goto(`/admin/application/workspace/${applicationId}/SIMPLE/access`)
    await expect(page).toHaveURL(new RegExp(`/application/workspace/${applicationId}/SIMPLE/access`))
    await expect(page.getByRole('heading', { name: ACCESS_HEADING })).toBeVisible()
  })
})
