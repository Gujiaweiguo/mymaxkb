import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  route: {
    path: '/application/workspace/app-1/overview',
    params: { id: 'app-1' },
  },
  getOrchestratorIntegration: vi.fn(),
  copyClick: vi.fn(),
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
    getOrchestratorIntegration: mocks.getOrchestratorIntegration,
  })),
}))

vi.mock('@/locales', () => ({
  t: (key: string) => key,
}))

import OrchestratorIntegrationPanel from '@/views/application-overview/component/OrchestratorIntegrationPanel.vue'
import { flushView, mountView } from '../helpers/view'

describe('Application overview Orchestrator integration panel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.getOrchestratorIntegration.mockResolvedValue({
      data: {
        endpoint_url: 'http://localhost:3080/api/knowledge',
        auth_token: 'agent-abc123',
        default_params: {
          kb_scope: ['uuid1', 'uuid2'],
          top_n: 5,
          similarity: 0.7,
        },
      },
    })
  })

  it('renders orchestrator integration values from the backend payload', async () => {
    const wrapper = mountView(OrchestratorIntegrationPanel)

    await flushView()

    expect(mocks.getOrchestratorIntegration).toHaveBeenCalledWith('app-1', expect.any(Object))
    expect(wrapper.text()).toContain('views.applicationOverview.appInfo.orchestratorIntegration')
    expect(wrapper.text()).toContain('http://localhost:3080/api/knowledge')
    expect(wrapper.text()).toContain('agent-abc123')
    expect(wrapper.text()).toContain('"kb_scope": [')
    expect(wrapper.text()).toContain('"top_n": 5')
    expect(wrapper.text()).toContain('"similarity": 0.7')
  })

  it('copies the full integration payload as formatted json', async () => {
    const wrapper = mountView(OrchestratorIntegrationPanel)

    await flushView()

    const buttons = wrapper.findAll('button')

    expect(buttons).toHaveLength(1)

    await buttons[0].trigger('click')

    expect(mocks.copyClick).toHaveBeenCalledWith(`{
  "endpoint_url": "http://localhost:3080/api/knowledge",
  "auth_token": "agent-abc123",
  "default_params": {
    "kb_scope": [
      "uuid1",
      "uuid2"
    ],
    "top_n": 5,
    "similarity": 0.7
  }
}`)
  })
})
