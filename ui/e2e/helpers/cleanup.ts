import type { Page } from '@playwright/test'

import type { TrackedResource } from './data'

type AdminSession = {
  token: string
  workspaceId: string
}

const DEFAULT_ADMIN_API_BASE = 'http://localhost:3000/admin/api'

function getAdminApiBaseUrl(): string {
  return process.env.E2E_ADMIN_API_BASE || DEFAULT_ADMIN_API_BASE
}

async function getAdminSession(page: Page): Promise<AdminSession> {
  const session = await page.evaluate(() => {
    const token = localStorage.getItem('token')
    const workspaceId = localStorage.getItem('workspace_id') || 'default'
    return { token, workspaceId }
  })

  if (!session.token) {
    throw new Error('Missing admin token for cleanup')
  }

  return session
}

async function deleteResource(session: AdminSession, type: TrackedResource['type'], id: string): Promise<boolean> {
  const base = getAdminApiBaseUrl()
  const paths: Record<TrackedResource['type'], string> = {
    user: `/system/user/${id}`,
    workspace: `/system/workspace/${id}`,
    application: `/workspace/${session.workspaceId}/application/${id}`,
    knowledge: `/workspace/${session.workspaceId}/knowledge/${id}`,
    model: `/workspace/${session.workspaceId}/model/${id}`,
    tool: `/workspace/${session.workspaceId}/tool/${id}`,
    document: `/workspace/${session.workspaceId}/knowledge/${id}`,
  }

  const path = paths[type]
  if (!path) {
    return false
  }

  try {
    const response = await fetch(`${base}${path}`, {
      method: 'DELETE',
      headers: {
        AUTHORIZATION: `Bearer ${session.token}`,
        'Accept-Language': 'en-US',
      },
    })

    return response.ok || response.status === 404
  } catch {
    return false
  }
}

export async function cleanupResources(page: Page, resources: TrackedResource[]): Promise<void> {
  if (resources.length === 0) {
    return
  }

  const session = await getAdminSession(page)
  const results = await Promise.allSettled(
    resources.map((resource) => deleteResource(session, resource.type, resource.id))
  )

  const failed = results.filter((r) => r.status === 'rejected' || (r.status === 'fulfilled' && !r.value))
  if (failed.length > 0) {
    console.warn(`Cleanup: ${failed.length} resource(s) could not be deleted`)
  }
}

export async function cleanupByType(
  page: Page,
  resources: TrackedResource[],
  type: TrackedResource['type']
): Promise<void> {
  const filtered = resources.filter((r) => r.type === type)
  await cleanupResources(page, filtered)
}
