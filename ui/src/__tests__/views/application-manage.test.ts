import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  route: { path: '/application/workspace', params: {}, query: {} },
  routerPush: vi.fn(),
  routerResolve: vi.fn(({ path }: { path: string }) => ({ href: path })),
  permissionMap: {
    application: {
      workspace: {
        create: vi.fn(() => true),
        edit: vi.fn(() => true),
        auth: vi.fn(() => true),
        export: vi.fn(() => true),
        delete: vi.fn(() => true),
        trigger_read: vi.fn(() => true),
      },
    },
  },
  hasPermission: vi.fn(() => true),
  getApplication: vi.fn(),
  getApplicationDetail: vi.fn(),
  getAccessToken: vi.fn(),
  delApplication: vi.fn(),
  exportApplication: vi.fn(),
  importApplication: vi.fn(),
  getAllMemberList: vi.fn(),
  MsgSuccess: vi.fn(),
  MsgConfirm: vi.fn(() => Promise.resolve()),
  MsgError: vi.fn(),
}))

vi.mock('vue-router', async (importOriginal) => {
  const actual = await importOriginal<typeof import('vue-router')>()

  return {
    ...actual,
    useRouter: () => ({
      push: mocks.routerPush,
      resolve: mocks.routerResolve,
    }),
    useRoute: () => mocks.route,
  }
})

vi.mock('@/permission', () => ({
  default: mocks.permissionMap,
}))

vi.mock('@/utils/permission', () => ({
  hasPermission: mocks.hasPermission,
}))

vi.mock('@/api/application/application', () => ({
  default: {
    getApplication: mocks.getApplication,
    getApplicationDetail: mocks.getApplicationDetail,
    getAccessToken: mocks.getAccessToken,
    delApplication: mocks.delApplication,
    exportApplication: mocks.exportApplication,
    importApplication: mocks.importApplication,
  },
}))

vi.mock('@/api/workspace/workspace', () => ({
  default: {
    getAllMemberList: mocks.getAllMemberList,
  },
}))

vi.mock('@/utils/message', () => ({
  MsgSuccess: mocks.MsgSuccess,
  MsgConfirm: mocks.MsgConfirm,
  MsgError: mocks.MsgError,
}))

vi.mock('@/views/application/component/CreateApplicationDialog.vue', () => ({
  default: { name: 'CreateApplicationDialog', template: '<div />' },
}))

vi.mock('@/components/folder-tree/CreateFolderDialog.vue', () => ({
  default: { name: 'CreateFolderDialog', template: '<div />' },
}))

vi.mock('@/views/application/component/CopyApplicationDialog.vue', () => ({
  default: { name: 'CopyApplicationDialog', template: '<div />' },
}))

vi.mock('@/components/folder-tree/MoveToDialog.vue', () => ({
  default: { name: 'MoveToDialog', template: '<div />' },
}))

vi.mock('@/components/resource-authorization-drawer/index.vue', () => ({
  default: { name: 'ResourceAuthorizationDrawer', template: '<div />' },
}))

vi.mock('@/views/trigger/ResourceTriggerDrawer.vue', () => ({
  default: { name: 'ResourceTriggerDrawer', template: '<div />' },
}))

vi.mock('@/views/application/template-store/TemplateStoreDialog.vue', () => ({
  default: { name: 'TemplateStoreDialog', template: '<div />' },
}))

import useStore from '../../stores'
import { SourceTypeEnum } from '../../enums/common'
import ApplicationManageView from '../../views/application/index.vue'
import { activateTestPinia, flushView, mountView } from '../helpers/view'

describe('Application Management View', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    activateTestPinia()

    const { folder, user } = useStore()

    folder.currentFolder = {}
    vi.spyOn(folder, 'asyncGetFolder').mockResolvedValue({
      data: [
        { id: 'default', name: 'All applications' },
        { id: 'folder-2', name: 'Operations' },
      ],
    })
    vi.spyOn(user, 'getWorkspaceId').mockReturnValue('workspace-1')

    mocks.getApplication.mockResolvedValue({
      data: {
        total: 2,
        records: [
          {
            id: 'app-1',
            name: 'Customer Support Bot',
            desc: 'Answers customer questions',
            nick_name: 'Ada',
            type: 'SIMPLE',
            is_publish: true,
            update_time: '2026-03-27 10:00:00',
            create_time: '2026-03-26 09:00:00',
          },
          {
            id: 'app-2',
            name: 'Workflow Builder',
            desc: 'Runs orchestrated workflows',
            nick_name: 'Grace',
            type: 'WORK_FLOW',
            is_publish: false,
            update_time: '2026-03-25 08:00:00',
            create_time: '2026-03-24 07:00:00',
          },
        ],
      },
    })
    mocks.getAllMemberList.mockResolvedValue({
      data: [{ id: 'user-1', nick_name: 'Ada' }],
    })
  })

  it('loads folders, applications, and workspace members on mount', async () => {
    const wrapper = mountView(ApplicationManageView)

    await flushView()

    const { folder } = useStore()

    expect(folder.asyncGetFolder).toHaveBeenCalledWith(
      SourceTypeEnum.APPLICATION,
      {},
      'workspace',
      expect.any(Object),
    )
    expect(mocks.getApplication).toHaveBeenCalledWith(
      expect.objectContaining({ current_page: 1, page_size: 30 }),
      { folder_id: 'default' },
      expect.any(Object),
    )
    expect(mocks.getAllMemberList).toHaveBeenCalledWith('workspace-1', expect.any(Object))
    expect(wrapper.text()).toContain('Customer Support Bot')
    expect(wrapper.text()).toContain('Workflow Builder')
  })

  it('reloads the list when a different folder is selected', async () => {
    const wrapper = mountView(ApplicationManageView)

    await flushView()
    await wrapper.get('[data-test="folder-node-folder-2"]').trigger('click')
    await flushView()

    expect(useStore().folder.currentFolder.id).toBe('folder-2')
    expect(mocks.getApplication).toHaveBeenLastCalledWith(
      expect.objectContaining({ current_page: 1, page_size: 30 }),
      { folder_id: 'folder-2' },
      expect.any(Object),
    )
  })

  it('routes to the resolved application page when a card is clicked', async () => {
    const wrapper = mountView(ApplicationManageView)

    await flushView()
    await wrapper.findAll('[data-test="card-box"]')[0].trigger('click')

    expect(mocks.routerPush).toHaveBeenCalledWith({
      path: '/application/workspace/app-1/SIMPLE/overview',
    })
  })
})
