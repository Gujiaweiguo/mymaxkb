import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  route: {
    path: '/application/workspace/app-1/overview',
    params: { id: 'app-1' },
  },
  getApplicationDetail: vi.fn(),
  getAccessToken: vi.fn(),
  getOrchestratorIntegration: vi.fn(),
  getStatistics: vi.fn(),
  getTokenUsage: vi.fn(),
  topQuestions: vi.fn(),
  copyClick: vi.fn(),
  MsgSuccess: vi.fn(),
  MsgConfirm: vi.fn(() => Promise.resolve()),
}))

vi.mock('vue-router', async (importOriginal) => {
  const actual = await importOriginal<typeof import('vue-router')>()

  return {
    ...actual,
    useRoute: () => mocks.route,
  }
})

vi.mock('@/utils/clipboard', () => ({
  copyClick: mocks.copyClick,
}))

vi.mock('@/utils/dynamics-api/shared-api', () => ({
  loadSharedApi: vi.fn(() => ({
    getApplicationDetail: mocks.getApplicationDetail,
    getAccessToken: mocks.getAccessToken,
    getOrchestratorIntegration: mocks.getOrchestratorIntegration,
    getStatistics: mocks.getStatistics,
    getTokenUsage: mocks.getTokenUsage,
    topQuestions: mocks.topQuestions,
  })),
}))

vi.mock('@/utils/common', () => ({
  getChatApiBaseUrl: vi.fn(() => 'http://localhost:3080/api/application'),
  getChatBaseUrl: vi.fn(() => 'http://localhost:3080/chat'),
  resetUrl: vi.fn((value: string) => value),
}))

vi.mock('@/utils/application', () => ({
  mapToUrlParams: vi.fn(() => ''),
}))

vi.mock('@/utils/time', () => ({
  nowDate: '2026-04-19',
  beforeDay: vi.fn(() => '2026-04-12'),
}))

vi.mock('@/utils/message', () => ({
  MsgSuccess: mocks.MsgSuccess,
  MsgConfirm: mocks.MsgConfirm,
}))

vi.mock('@/utils/permission/index', () => ({
  hasPermission: vi.fn(() => false),
}))

vi.mock('@/permission', () => ({
  default: {
    application: {
      workspace: {
        overview_api_key: vi.fn(() => true),
        overview_embed: vi.fn(() => true),
        overview_access: vi.fn(() => true),
        overview_display: vi.fn(() => true),
      },
      systemManage: {
        overview_api_key: vi.fn(() => true),
        overview_embed: vi.fn(() => true),
        overview_access: vi.fn(() => true),
        overview_display: vi.fn(() => true),
      },
    },
  },
}))

vi.mock('@/locales', () => ({
  t: (key: string) => key,
}))

import { flushView, mountView } from '../helpers/view'

async function mountOverview() {
  const { default: ApplicationOverview } = await vi.importActual<any>(
    '@/views/application-overview/index.vue',
  )

  return mountView(ApplicationOverview)
}

function getButtonByText(
  wrapper: Awaited<ReturnType<typeof mountOverview>>,
  text: string,
) {
  return wrapper.findAll('button').find((button) => button.text().includes(text))
}

describe('Application overview orchestrator config', () => {
  beforeEach(() => {
    vi.clearAllMocks()

    mocks.getApplicationDetail.mockResolvedValue({
      data: {
        name: 'Overview app',
        icon: '/icon.png',
        work_flow: {
          nodes: [],
        },
      },
    })
    mocks.getAccessToken.mockResolvedValue({
      data: {
        access_token: 'share-token',
        is_active: true,
      },
    })
    mocks.getOrchestratorIntegration.mockResolvedValue({
      data: {
        endpoint_url: 'http://localhost:3080/api/orchestrator',
        auth_token: 'orch-token-123',
        default_params: {
          kb_scope: ['kb-1', 'kb-2'],
          top_n: 5,
          similarity: 0.7,
        },
      },
    })
    mocks.getStatistics.mockResolvedValue({ data: [] })
    mocks.getTokenUsage.mockResolvedValue({ data: [] })
    mocks.topQuestions.mockResolvedValue({ data: [] })
  })

  it('renders the orchestrator config section with endpoint, token, and default params', async () => {
    const wrapper = await mountOverview()

    await flushView()

    expect(mocks.getOrchestratorIntegration).toHaveBeenCalledWith('app-1')
    expect(wrapper.text()).toContain('Orchestrator Integration')
    expect(wrapper.text()).toContain('http://localhost:3080/api/orchestrator')
    expect(wrapper.text()).toContain('orch-token-123')
    expect(wrapper.text()).toContain('"kb_scope": [')
    expect(wrapper.text()).toContain('"top_n": 5')
    expect(wrapper.text()).toContain('"similarity": 0.7')
  })

  it('copies the full orchestrator config payload as formatted json', async () => {
    const wrapper = await mountOverview()

    await flushView()

    const copyAllButton = getButtonByText(wrapper, 'Copy Integration Config')

    expect(copyAllButton).toBeTruthy()

    await copyAllButton?.trigger('click')

    expect(mocks.copyClick).toHaveBeenCalledWith(`{
  "endpoint_url": "http://localhost:3080/api/orchestrator",
  "auth_token": "orch-token-123",
  "default_params": {
    "kb_scope": [
      "kb-1",
      "kb-2"
    ],
    "top_n": 5,
    "similarity": 0.7
  }
}`)
  })
})
