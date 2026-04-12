import { beforeEach, describe, expect, it, vi } from 'vitest'
import { defineComponent, h } from 'vue'

const mocks = vi.hoisted(() => ({
  getUserManage: vi.fn(),
  putUserManage: vi.fn(),
  delUserManage: vi.fn(),
  batchDelete: vi.fn(),
  userDrawerOpen: vi.fn(),
  MsgSuccess: vi.fn(),
  MsgConfirm: vi.fn(() => Promise.resolve()),
  hasPermission: vi.fn(() => true),
}))

vi.mock('@/api/system/user-manage', () => ({
  default: {
    getUserManage: mocks.getUserManage,
    putUserManage: mocks.putUserManage,
    delUserManage: mocks.delUserManage,
    batchDelete: mocks.batchDelete,
  },
}))

vi.mock('@/utils/message', () => ({
  MsgSuccess: mocks.MsgSuccess,
  MsgConfirm: mocks.MsgConfirm,
}))

vi.mock('@/utils/permission/index', () => ({
  hasPermission: mocks.hasPermission,
}))

vi.mock('@/views/system/user-manage/component/UserDrawer.vue', () => ({
  default: defineComponent({
    name: 'UserDrawer',
    setup(_, { expose }) {
      expose({ open: mocks.userDrawerOpen })
      return () => h('div', { 'data-test': 'user-drawer-stub' })
    },
  }),
}))

vi.mock('@/views/system/user-manage/component/UserPwdDialog.vue', () => ({
  default: { name: 'UserPwdDialog', template: '<div />' },
}))

vi.mock('@/views/system/user-manage/component/SetUserRoleDialog.vue', () => ({
  default: { name: 'SetUserRoleDialog', template: '<div />' },
}))

import useStore from '../../stores'
import UserManageView from '../../views/system/user-manage/index.vue'
import { activateTestPinia, flushView, mountView } from '../helpers/view'

const AppTableStub = defineComponent({
  name: 'AppTableStub',
  setup() {
    return () => h('div', { 'data-test': 'app-table-stub' })
  },
})

function mountUserManageView() {
  return mountView(UserManageView, {
    global: {
      stubs: {
        'app-table': AppTableStub,
        UserDrawer: false,
        UserPwdDialog: false,
        SetUserRoleDialog: false,
      },
    },
  })
}

describe('User Management View', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    activateTestPinia()

    const { user } = useStore()
    user.userInfo = { id: 'current-user', role: ['ADMIN'] } as any
    user.edition = 'CE'
    user.license_is_valid = false

    mocks.getUserManage.mockResolvedValue({
      data: {
        total: 2,
        records: [
          {
            id: 'user-1',
            username: 'alice',
            nick_name: 'Alice',
            email: 'alice@example.com',
            phone: '',
            is_active: true,
            source: 'LOCAL',
            role_name: ['系统管理员'],
            role_workspace: { ADMIN: ['None'] },
            create_time: '2026-04-01 10:00:00',
          },
          {
            id: 'user-2',
            username: 'bob',
            nick_name: 'Bob',
            email: 'bob@example.com',
            phone: '',
            is_active: false,
            source: 'LOCAL',
            role_name: ['普通用户'],
            role_workspace: { USER: ['default'] },
            create_time: '2026-04-01 11:00:00',
          },
        ],
      },
    })
    mocks.delUserManage.mockResolvedValue({ data: true })
  })

  it('loads the user list on mount and normalizes role workspace display', async () => {
    const wrapper = mountUserManageView()

    await flushView()

    expect(mocks.getUserManage).toHaveBeenCalledWith(
      expect.objectContaining({ current_page: 1, page_size: 20 }),
      {},
      expect.any(Object),
    )
    expect((wrapper.vm as any).userTableData).toHaveLength(2)
    expect((wrapper.vm as any).userTableData[0].role_workspace[0]).toEqual({
      role: 'ADMIN',
      workspace: '-',
    })
  })

  it('reloads the list with the selected search field when the search input changes', async () => {
    const wrapper = mountUserManageView()

    await flushView()
    await wrapper.get('select').setValue('email')
    await wrapper.get('input[placeholder="common.inputPlaceholder"]').setValue('alice@example.com')
    await wrapper.get('input[placeholder="common.inputPlaceholder"]').trigger('change')
    await flushView()

    expect(mocks.getUserManage).toHaveBeenLastCalledWith(
      expect.objectContaining({ current_page: 1, page_size: 20 }),
      { email: 'alice@example.com' },
      expect.any(Object),
    )
  })

  it('opens the create-user drawer from the real toolbar action', async () => {
    const wrapper = mountUserManageView()

    await flushView()
    await wrapper.get('button').trigger('click')
    await flushView()

    expect(mocks.userDrawerOpen).toHaveBeenCalledWith()
    expect((wrapper.vm as any).title).toBe('Create User')
  })
})
