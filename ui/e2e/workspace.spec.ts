import { testWithCleanup as test, expect } from './fixtures'

import { loginAsAdmin } from './helpers/auth'
import { uniqueWorkspaceName } from './helpers/data'

async function trackCreatedWorkspace(page, resourceTracker, workspaceName: string) {
  let workspaceId: string | null = null

  await expect
    .poll(async () => {
      workspaceId = await page.evaluate(async (targetName) => {
        const token = localStorage.getItem('token')
        if (!token) {
          return null
        }

        const response = await fetch('/admin/api/workspace', {
          headers: {
            AUTHORIZATION: `Bearer ${token}`,
            'Accept-Language': 'en-US',
          },
        })

        const body = await response.json()
        return body?.data?.find((item) => item.name === targetName)?.id ?? null
      }, workspaceName)

      return workspaceId
    }, { timeout: 15000 })
    .toBeTruthy()

  resourceTracker.track({ type: 'workspace', id: workspaceId!, name: workspaceName })
}

test.describe('@advisory Workspace Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/system/workspace')
  })

  test('should navigate to the workspace page', async ({ page }) => {
    await expect(page).toHaveURL(/\/admin\/system\/workspace(?:$|\?|\/)/)
    await expect(page.locator('.workspace-manage')).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Workspace', exact: true })).toBeVisible()
  })

  test('should display workspace panels and search input', async ({ page }) => {
    await expect(page.locator('.workspace-left')).toBeVisible()
    await expect(page.locator('.workspace-right')).toBeVisible()
    await expect(page.getByPlaceholder('Search')).toBeVisible()
  })

  test('should create, switch, rename, search, and delete a workspace', async ({ page, resourceTracker }) => {
    const workspaceList = page.locator('.workspace-left')
    const originalWorkspaceName = (await page.locator('.workspace-right h4').first().textContent())?.trim()
    const workspaceName = uniqueWorkspaceName()
    const renamedWorkspaceName = `${workspaceName} Renamed`

    await page.locator('.workspace-left .el-button').first().click()

    const createDialog = page.locator('.el-dialog').filter({ has: page.getByRole('button', { name: 'Create' }) })
    await expect(createDialog).toBeVisible()
    await createDialog.getByPlaceholder('Please inputWorkspace name').fill(workspaceName)
    await createDialog.getByRole('button', { name: 'Create' }).click()

    await trackCreatedWorkspace(page, resourceTracker, workspaceName)
    await expect(page.locator('.workspace-right h4').first()).toHaveText(workspaceName)

    if (originalWorkspaceName && originalWorkspaceName !== workspaceName) {
      await workspaceList.getByTitle(originalWorkspaceName).click()
      await expect(page.locator('.workspace-right h4').first()).toHaveText(originalWorkspaceName)
    }

    await workspaceList.getByTitle(workspaceName).click()
    await expect(page.locator('.workspace-right h4').first()).toHaveText(workspaceName)

    await page.getByPlaceholder('Search').fill(workspaceName)
    await expect(workspaceList.getByTitle(workspaceName)).toBeVisible()
    await page.getByPlaceholder('Search').clear()

    const workspaceRow = workspaceList.getByTitle(workspaceName).locator('..')
    await workspaceRow.hover()
    await workspaceRow.locator('.el-dropdown').getByRole('button').click()
    await page.getByRole('menuitem', { name: 'Rename' }).last().click()

    const renameDialog = page.locator('.el-dialog').filter({ has: page.getByRole('button', { name: 'Save' }) })
    await expect(renameDialog).toBeVisible()
    await renameDialog.getByPlaceholder('Please inputWorkspace name').fill(renamedWorkspaceName)
    await renameDialog.getByRole('button', { name: 'Save' }).click()

    await expect(page.locator('.workspace-right h4').first()).toHaveText(renamedWorkspaceName)

    await page.getByPlaceholder('Search').fill(renamedWorkspaceName)
    const renamedWorkspaceRow = workspaceList.getByTitle(renamedWorkspaceName).locator('..')
    await renamedWorkspaceRow.hover()
    await renamedWorkspaceRow.locator('.el-dropdown').getByRole('button').click()
    await page.getByRole('menuitem', { name: 'Delete' }).last().click()

    const confirmDialog = page.locator('.el-message-box').last()
    await expect(confirmDialog).toBeVisible()
    await confirmDialog.getByRole('button', { name: 'OK' }).click()

    await expect(workspaceList.getByTitle(renamedWorkspaceName)).toBeHidden()
    resourceTracker.clear()
  })
})
