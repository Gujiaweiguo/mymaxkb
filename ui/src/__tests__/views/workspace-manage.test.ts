import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => {
  const workspaceApi = {
    getSystemWorkspaceList: vi.fn(),
    deleteWorkspaceCheck: vi.fn(),
    deleteWorkspace: vi.fn(),
  }

  return {
    workspaceApi,
    loadPermissionApi: vi.fn(() => workspaceApi),
    hasPermission: vi.fn(() => true),
    MsgSuccess: vi.fn(),
    MsgConfirm: vi.fn(() => Promise.resolve()),
  }
})

vi.mock('@/utils/dynamics-api/permission-api.ts', () => ({
  loadPermissionApi: mocks.loadPermissionApi,
}))

vi.mock('@/utils/permission/index', () => ({
  hasPermission: mocks.hasPermission,
}))

vi.mock('@/utils/message', () => ({
  MsgSuccess: mocks.MsgSuccess,
  MsgConfirm: mocks.MsgConfirm,
}))

import WorkspaceManageView from '../../views/system/workspace/index.vue'
import { flushView, mountView } from '../helpers/view'

describe('Workspace Management View', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.loadPermissionApi.mockImplementation(() => mocks.workspaceApi)
    mocks.workspaceApi.getSystemWorkspaceList.mockResolvedValue({
      data: [
        { id: 'alpha', name: 'Alpha Workspace', user_count: 12 },
        { id: 'beta', name: 'Beta Workspace', user_count: 3 },
      ],
    })
  })

  it('loads the workspace list and selects the first workspace on mount', async () => {
    const wrapper = mountView(WorkspaceManageView)

    await flushView()

    expect(mocks.loadPermissionApi).toHaveBeenCalledWith('workspace')
    expect(mocks.workspaceApi.getSystemWorkspaceList).toHaveBeenCalledWith(expect.any(Object))
    expect(wrapper.findAll('h4')[1].text()).toBe('Alpha Workspace')
  })

  it('filters the workspace list from the search input', async () => {
    const wrapper = mountView(WorkspaceManageView)

    await flushView()
    await wrapper.get('input[placeholder="common.search"]').setValue('beta')
    await flushView()

    expect(wrapper.find('[data-test="common-list-item-alpha"]').exists()).toBe(false)
    expect(wrapper.get('[data-test="common-list-item-beta"]').text()).toContain('Beta Workspace')
  })

  it('updates the detail panel when a workspace is selected', async () => {
    const wrapper = mountView(WorkspaceManageView)

    await flushView()
    await wrapper.get('[data-test="common-list-item-beta"]').trigger('click')
    await flushView()

    expect(wrapper.findAll('h4')[1].text()).toBe('Beta Workspace')
  })
})
