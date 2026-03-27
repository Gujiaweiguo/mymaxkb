import { randomUUID } from 'node:crypto'
import { readFile } from 'node:fs/promises'

import { expect, type Page } from '@playwright/test'

import { loginAsAdmin } from './auth'
import type { ResourceTracker } from './data'

const DEFAULT_WORKSPACE_ID = 'default'
const DEFAULT_SILICONCLOUD_BASE = 'https://api.siliconflow.cn/v1'
const DEFAULT_SILICONCLOUD_MODEL = 'Qwen/Qwen2.5-7B-Instruct'
const DEFAULT_ADMIN_API_BASE = 'http://localhost:3000/admin/api'
const DEFAULT_CHAT_BASE_URL = 'http://localhost:3001'

type ChatProviderConfig = {
  apiBase: string
  apiKey: string
  modelName: string
  provider: 'model_siliconCloud_provider'
}

type AdminSession = {
  token: string
  workspaceId: string
}

type ApiResult<T> = {
  code: number
  message: string
  data: T
}

let cachedChatProviderConfig: ChatProviderConfig | null | undefined

function parseEnvFile(content: string) {
  return content.split('\n').reduce<Record<string, string>>((acc, line) => {
    const trimmed = line.trim()
    if (!trimmed || trimmed.startsWith('#')) {
      return acc
    }

    const separatorIndex = trimmed.indexOf('=')
    if (separatorIndex === -1) {
      return acc
    }

    const key = trimmed.slice(0, separatorIndex).trim()
    const rawValue = trimmed.slice(separatorIndex + 1).trim()
    acc[key] = rawValue.replace(/^['"]|['"]$/g, '')
    return acc
  }, {})
}

async function loadLocalDevEnv() {
  try {
    const envText = await readFile(new URL('../../../.env.local-dev', import.meta.url), 'utf8')
    return parseEnvFile(envText)
  } catch {
    return {}
  }
}

export async function getChatProviderConfig() {
  if (cachedChatProviderConfig !== undefined) {
    return cachedChatProviderConfig
  }

  const localEnv = await loadLocalDevEnv()
  const apiKey = process.env.SILICONCLOUD_API_KEY || localEnv.SILICONCLOUD_API_KEY

  if (!apiKey) {
    cachedChatProviderConfig = null
    return cachedChatProviderConfig
  }

  cachedChatProviderConfig = {
    provider: 'model_siliconCloud_provider',
    apiBase:
      process.env.SILICONCLOUD_API_BASE ||
      localEnv.SILICONCLOUD_API_BASE ||
      DEFAULT_SILICONCLOUD_BASE,
    apiKey,
    modelName: process.env.E2E_CHAT_MODEL_NAME || DEFAULT_SILICONCLOUD_MODEL,
  }

  return cachedChatProviderConfig
}

function getAdminApiBaseUrl() {
  return process.env.E2E_ADMIN_API_BASE || DEFAULT_ADMIN_API_BASE
}

function getChatBaseUrl() {
  return process.env.E2E_CHAT_BASE_URL || DEFAULT_CHAT_BASE_URL
}

async function getAdminSession(page: Page): Promise<AdminSession> {
  const session = await page.evaluate(() => {
    const token = localStorage.getItem('token')
    const workspaceId = localStorage.getItem('workspace_id') || 'default'

    return {
      token,
      workspaceId,
    }
  })

  if (!session.token) {
    throw new Error('Missing admin token after login')
  }

  return {
    token: session.token,
    workspaceId: session.workspaceId || DEFAULT_WORKSPACE_ID,
  }
}

async function callAdminApi<T>(session: AdminSession, path: string, init?: RequestInit): Promise<ApiResult<T>> {
  const response = await fetch(`${getAdminApiBaseUrl()}${path}`, {
    ...init,
    headers: {
      AUTHORIZATION: `Bearer ${session.token}`,
      'Accept-Language': 'en-US',
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
  })

  const json = (await response.json()) as ApiResult<T>
  if (!response.ok || json.code !== 200) {
    throw new Error(`Admin API ${path} failed: ${response.status} ${JSON.stringify(json)}`)
  }

  return json
}

async function createRemoteChatModel(session: AdminSession, config: ChatProviderConfig) {
  const name = `E2E SiliconCloud Chat ${randomUUID()}`
  const response = await callAdminApi<{ id: string }>(session, `/workspace/${session.workspaceId}/model`, {
    method: 'POST',
    body: JSON.stringify({
      name,
      provider: config.provider,
      model_type: 'LLM',
      model_name: config.modelName,
      credential: {
        api_base: config.apiBase,
        api_key: config.apiKey,
      },
      model_params_form: [],
    }),
  })

  return response.data.id
}

async function createPublishedChatApplication(session: AdminSession, modelId: string) {
  const response = await callAdminApi<{ id: string }>(session, `/workspace/${session.workspaceId}/application`, {
    method: 'POST',
    body: JSON.stringify({
      name: `E2E Remote Chat ${randomUUID()}`,
      desc: 'Remote-provider-backed Playwright chat smoke test',
      model_id: modelId,
      dialogue_number: 1,
      prologue: 'Hello from remote chat smoke test.',
      knowledge_id_list: [],
      knowledge_setting: {
        top_n: 3,
        similarity: 0.6,
        max_paragraph_char_number: 5000,
        search_mode: 'embedding',
        no_references_setting: {
          status: 'ai_questioning',
          value: '{question}',
        },
      },
      model_setting: {
        prompt: 'Known information: {data}\nUser question: {question}',
        system: '',
        no_references_prompt: '{question}',
      },
      model_params_setting: {},
      problem_optimization: false,
      problem_optimization_prompt: 'Question: {question}<data></data>',
      stt_model_id: null,
      tts_model_id: null,
      stt_model_enable: false,
      tts_model_enable: false,
      tts_type: 'BROWSER',
      type: 'SIMPLE',
      folder_id: DEFAULT_WORKSPACE_ID,
    }),
  })

  const applicationId = response.data.id

  await callAdminApi(session, `/workspace/${session.workspaceId}/application/${applicationId}/publish`, {
    method: 'PUT',
    body: JSON.stringify({}),
  })

  return applicationId
}

async function getApplicationAccessToken(session: AdminSession, applicationId: string) {
  const response = await callAdminApi<{ access_token: string }>(
    session,
    `/workspace/${session.workspaceId}/application/${applicationId}/access_token`,
  )

  return response.data.access_token
}

export type ProvisionedChatResources = {
  accessToken: string
  chatUrl: string
  modelId: string
  applicationId: string
}

export async function provisionRemoteChatAccess(page: Page): Promise<ProvisionedChatResources> {
  const config = await getChatProviderConfig()
  if (!config) {
    throw new Error('Missing SiliconCloud configuration. Set SILICONCLOUD_API_KEY in .env.local-dev.')
  }

  await loginAsAdmin(page)
  const session = await getAdminSession(page)
  const modelId = await createRemoteChatModel(session, config)
  const applicationId = await createPublishedChatApplication(session, modelId)
  const accessToken = await getApplicationAccessToken(session, applicationId)

  return {
    accessToken,
    chatUrl: `${getChatBaseUrl()}/${accessToken}?mode=pc`,
    modelId,
    applicationId,
  }
}

export async function provisionRemoteChatAccessWithCleanup(
  page: Page,
  resourceTracker: ResourceTracker
): Promise<ProvisionedChatResources> {
  const resources = await provisionRemoteChatAccess(page)
  
  resourceTracker.track({ type: 'model', id: resources.modelId })
  resourceTracker.track({ type: 'application', id: resources.applicationId })
  
  return resources
}

export async function expectChatShell(page: Page) {
  await expect(page.locator('.chat-pc')).toBeVisible()
  await expect(page.locator('.not-found-container')).toHaveCount(0)
  await expect(page).not.toHaveURL(/\/no-service(?:$|\?|\/)/)
}
