import { testWithCleanup as test, expect } from './fixtures'

import { loginAsAdmin } from './helpers/auth'
import { uniqueKnowledgeName } from './helpers/data'
import { getChatProviderConfig } from './helpers/chat'

const KNOWLEDGE_UPLOAD_FIXTURE = '/opt/code/mymaxkb/ui/e2e/fixtures/knowledge-upload.txt'
const DEFAULT_EMBEDDING_MODEL = 'BAAI/bge-m3'

async function ensureEmbeddingModel(page, resourceTracker) {
  return page.evaluate(
    async ({ providerConfig, embeddingModelName }) => {
      const token = localStorage.getItem('token')
      const workspaceId = localStorage.getItem('workspace_id') || 'default'
      if (!token) {
        throw new Error('Missing admin token while preparing embedding model')
      }

      const listResponse = await fetch(`/admin/api/workspace/${workspaceId}/knowledge/model`, {
        headers: {
          AUTHORIZATION: `Bearer ${token}`,
          'Accept-Language': 'en-US',
        },
      })
      const listBody = await listResponse.json()
      const existingModelId = listBody?.data?.[0]?.id
      if (existingModelId) {
        return { id: existingModelId, created: false }
      }

      if (!providerConfig) {
        throw new Error('No embedding model available and no SiliconCloud credentials configured')
      }

      const createResponse = await fetch(`/admin/api/workspace/${workspaceId}/model`, {
        method: 'POST',
        headers: {
          AUTHORIZATION: `Bearer ${token}`,
          'Accept-Language': 'en-US',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: `E2E Embedding ${Date.now()}`,
          provider: providerConfig.provider,
          model_type: 'EMBEDDING',
          model_name: embeddingModelName,
          credential: {
            api_base: providerConfig.apiBase,
            api_key: providerConfig.apiKey,
          },
          model_params_form: [],
        }),
      })

      const createBody = await createResponse.json()
      return { id: createBody?.data?.id ?? null, created: true }
    },
    {
      providerConfig: await getChatProviderConfig(),
      embeddingModelName: DEFAULT_EMBEDDING_MODEL,
    },
  ).then((model) => {
    expect(model?.id).toBeTruthy()
    if (model.created) {
      resourceTracker.track({ type: 'model', id: model.id })
    }
    return model.id as string
  })
}

async function hasAvailableEmbeddingPrerequisite(page) {
  const providerConfig = await getChatProviderConfig()
  if (providerConfig) {
    return true
  }

  return page.evaluate(async () => {
    const token = localStorage.getItem('token')
    const workspaceId = localStorage.getItem('workspace_id') || 'default'
    if (!token) {
      return false
    }

    const response = await fetch(`/admin/api/workspace/${workspaceId}/knowledge/model`, {
      headers: {
        AUTHORIZATION: `Bearer ${token}`,
        'Accept-Language': 'en-US',
      },
    })
    const body = await response.json()
    return Boolean(body?.data?.[0]?.id)
  })
}

async function getKnowledgeTarget(page, resourceTracker, knowledgeName: string) {
  const embeddingModelId = await ensureEmbeddingModel(page, resourceTracker)

  const knowledge = await page.evaluate(async ({ targetName, targetEmbeddingModelId }) => {
    const token = localStorage.getItem('token')
    const workspaceId = localStorage.getItem('workspace_id') || 'default'
    if (!token) {
      throw new Error('Missing admin token while creating knowledge base')
    }

    const headers = {
      AUTHORIZATION: `Bearer ${token}`,
      'Accept-Language': 'en-US',
      'Content-Type': 'application/json',
    }

    if (targetEmbeddingModelId) {
      const createResponse = await fetch(`/admin/api/workspace/${workspaceId}/knowledge/base`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          folder_id: 'default',
          name: targetName,
          desc: 'E2E knowledge upload flow',
          embedding_model_id: targetEmbeddingModelId,
        }),
      })

      const createBody = await createResponse.json()
      return {
        id: createBody?.data?.id ?? null,
        created: true,
      }
    }

    const listResponse = await fetch(`/admin/api/workspace/${workspaceId}/knowledge?folder_id=default`, {
      headers: {
        AUTHORIZATION: `Bearer ${token}`,
        'Accept-Language': 'en-US',
      },
    })
    const listBody = await listResponse.json()
    const fallbackKnowledge = listBody?.data?.find((item) => item.type === 0) ?? null
    return {
      id: fallbackKnowledge?.id ?? null,
      created: false,
    }
  }, { targetName: knowledgeName, targetEmbeddingModelId: embeddingModelId })

  expect(knowledge?.id).toBeTruthy()
  if (knowledge.created) {
    resourceTracker.track({ type: 'knowledge', id: knowledge.id, name: knowledgeName })
  }
  return knowledge as { id: string; created: boolean }
}

async function deleteUploadedDocument(page, knowledgeId: string, documentName: string) {
  await page.evaluate(async ({ targetKnowledgeId, targetDocumentName }) => {
    const token = localStorage.getItem('token')
    const workspaceId = localStorage.getItem('workspace_id') || 'default'
    if (!token) {
      return
    }

    const listResponse = await fetch(
      `/admin/api/workspace/${workspaceId}/knowledge/${targetKnowledgeId}/document/1/10?name=${encodeURIComponent(targetDocumentName)}`,
      {
        headers: {
          AUTHORIZATION: `Bearer ${token}`,
          'Accept-Language': 'en-US',
        },
      },
    )
    const listBody = await listResponse.json()
    const documentId = listBody?.data?.records?.find((item) => item.name === targetDocumentName)?.id
    if (!documentId) {
      return
    }

    await fetch(`/admin/api/workspace/${workspaceId}/knowledge/${targetKnowledgeId}/document/${documentId}`, {
      method: 'DELETE',
      headers: {
        AUTHORIZATION: `Bearer ${token}`,
        'Accept-Language': 'en-US',
      },
    })
  }, { targetKnowledgeId: knowledgeId, targetDocumentName: documentName })
}

test.describe('@advisory Knowledge Base Management', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page)
    await page.goto('/admin/knowledge')
  })

  test('should navigate to the knowledge page', async ({ page }) => {
    await expect(page).toHaveURL(/\/admin\/knowledge(?:$|\?|\/)/)
    await expect(page.locator('.knowledge-manage')).toBeVisible()
  })

  test('should display knowledge heading and create control', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Knowledge' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Create' })).toBeVisible()
  })

  test('should upload a document into a knowledge base', async ({ page, resourceTracker }) => {
    test.skip(
      !(await hasAvailableEmbeddingPrerequisite(page)),
      'Requires an existing embedding model or SiliconCloud credentials to provision one.',
    )

    const knowledgeName = uniqueKnowledgeName()
    const { id: knowledgeId } = await getKnowledgeTarget(page, resourceTracker, knowledgeName)

    await page.goto(`/knowledge/${knowledgeId}/default/0/document`)
    await expect(page.getByRole('button', { name: 'Upload Document' })).toBeVisible()
    await page.getByRole('button', { name: 'Upload Document' }).click()

    await expect(page).toHaveURL(new RegExp(`/admin/knowledge/document/upload/default/0\\?id=${knowledgeId}$`))
    await expect(page.locator('.upload-document')).toContainText('Upload Document')

    await page.locator('.el-upload__input').setInputFiles(KNOWLEDGE_UPLOAD_FIXTURE)
    await expect(page.getByText('knowledge-upload.txt', { exact: true })).toBeVisible()

    await page.getByRole('button', { name: 'Next' }).click()
    await expect(page.getByText('Set Segment Rules', { exact: true })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Start Import' })).toBeVisible()

    await page.getByRole('button', { name: 'Start Import' }).click()
    await expect(page).toHaveURL(new RegExp(`/knowledge/${knowledgeId}/default/0/document`), {
      timeout: 15000,
    })

    const searchInput = page.getByPlaceholder('Search by name')
    await searchInput.fill('knowledge-upload.txt')
    await searchInput.blur()

    await expect(page.locator('tr', { hasText: 'knowledge-upload.txt' })).toBeVisible()
    await deleteUploadedDocument(page, knowledgeId, 'knowledge-upload.txt')
  })
})
