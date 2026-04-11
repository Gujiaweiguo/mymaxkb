import { testWithCleanup as test, expect } from './fixtures'

import { ADMIN_APPLICATION_URL, loginAsAdmin } from './helpers/auth'
import { uniqueApplicationName } from './helpers/data'

async function trackCreatedApplication(page, resourceTracker, applicationName: string) {
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
        return body?.data?.records?.find((item) => item.name === targetName)?.id ?? null
      }, applicationName)

      return applicationId
    }, { timeout: 15000 })
    .toBeTruthy()

  resourceTracker.track({ type: 'application', id: applicationId!, name: applicationName })
  return applicationId!
}

test.describe('@advisory Application Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
  })

  test('should land on the application page after login', async ({ page }) => {
    await expect(page).toHaveURL(ADMIN_APPLICATION_URL)
    await expect(page.locator('.application-manage')).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Agent' })).toBeVisible()
  })

  test('should display application search and create controls', async ({ page }) => {
    await expect(page.locator('.application-manage .complex-search')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Create' })).toBeVisible()
  })

  test('should open the create application menu', async ({ page }) => {
    await page.getByRole('button', { name: 'Create' }).click()

    await expect(page.getByText('Simple Agent', { exact: true })).toBeVisible()
    await expect(page.getByText('Advanced Agent', { exact: true })).toBeVisible()
    await expect(page.getByText('Import Agent', { exact: true })).toBeVisible()
  })

  test('should create an application and save configuration changes', async ({ page, resourceTracker }) => {
    const applicationName = uniqueApplicationName()
    const updatedDescription = `${applicationName} description updated in E2E`

    await page.getByRole('button', { name: 'Create' }).click()
    await page.getByText('Simple Agent', { exact: true }).click()

    const createDialog = page.locator('.el-dialog').filter({ has: page.getByRole('button', { name: 'Create' }) })
    await expect(createDialog).toBeVisible()
    await createDialog.getByPlaceholder('Please enter the agent name').fill(applicationName)
    await createDialog
      .getByPlaceholder('Describe the Agent scenario and use, e.g.: XXX assistant answering user questions about XXX product usage')
      .fill('E2E application configuration flow')
    await createDialog.getByRole('button', { name: 'Create' }).click()

    const applicationId = await trackCreatedApplication(page, resourceTracker, applicationName)
    await expect(page).toHaveURL(/\/application\/workspace\/[^/]+\/SIMPLE\/setting(?:$|\?|\/)/)
    await expect(page.locator('.application-setting')).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Setting' })).toBeVisible()
    await expect(page.getByPlaceholder('Please enter the agent name')).toHaveValue(applicationName)

    const descriptionInput = page.getByPlaceholder(
      'Describe the Agent scenario and use, e.g.: XXX assistant answering user questions about XXX product usage',
    )
    await descriptionInput.fill(updatedDescription)
    await page.getByRole('button', { name: 'Save' }).click()

    await page.goto('/admin/application')
    await expect(page).toHaveURL(ADMIN_APPLICATION_URL)

    const searchInput = page.getByPlaceholder('Search by name')
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
})
