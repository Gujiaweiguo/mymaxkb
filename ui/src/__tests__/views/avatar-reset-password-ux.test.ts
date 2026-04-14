import { beforeEach, describe, expect, it, vi } from 'vitest'
import { defineComponent, h } from 'vue'

const mocks = vi.hoisted(() => ({
  permissionValue: new Proxy(
    {},
    {
      get: () => 'permission-stub',
    },
  ),
  permissionGroup: null as unknown,
  routerPush: vi.fn(),
  clearToken: vi.fn(),
  resetCurrentPassword: vi.fn(() => Promise.resolve()),
  userInfo: {
    id: 'user-1',
    username: 'admin',
    nick_name: 'Admin',
    role_name: [],
    is_edit_password: false,
  },
}))

const hoistedPermissionGroup = vi.hoisted(() => {
  const permissionValue = new Proxy(
    {},
    {
      get: () => 'permission-stub',
    },
  )

  return new Proxy(
    {},
    {
      get: () => permissionValue,
    },
  )
})

vi.mock('vue-router', async (importOriginal) => {
  const actual = await importOriginal<typeof import('vue-router')>()

  return {
    ...actual,
    useRouter: () => ({
      push: mocks.routerPush,
    }),
  }
})

vi.mock('@/router', () => ({
  default: {
    push: mocks.routerPush,
  },
}))

vi.mock('@/stores', () => ({
  default: () => ({
    login: {
      clearToken: mocks.clearToken,
      logout: vi.fn(() => Promise.resolve()),
    },
    user: {
      userInfo: mocks.userInfo,
      postUserLanguage: vi.fn(),
    },
  }),
}))

vi.mock('@/layout/layout-header/avatar/AboutDialog.vue', () => ({
  default: {
    name: 'AboutDialogStub',
    methods: {
      open() {},
    },
    render() {
      return null
    },
  },
}))

vi.mock('@/layout/layout-header/avatar/APIKeyDialog.vue', () => ({
  default: {
    name: 'APIKeyDialogStub',
    methods: {
      open() {},
    },
    render() {
      return null
    },
  },
}))

vi.mock('@/api/user/user', () => ({
  default: {
    resetCurrentPassword: mocks.resetCurrentPassword,
  },
}))

vi.mock('@/locales', () => ({
  t: (key: string) => key,
}))

vi.mock('@/locales/index', () => ({
  t: (key: string) => key,
  langList: [],
}))

vi.mock('@/utils/permission', () => ({
  hasPermission: vi.fn(() => false),
}))

vi.mock('@/utils/permission/type', () => ({
  ComplexPermission: class ComplexPermission {},
}))

vi.mock('@/utils/permission/data', () => ({
  PermissionConst: hoistedPermissionGroup,
  RoleConst: hoistedPermissionGroup,
  EditionConst: hoistedPermissionGroup,
}))

vi.mock('@/utils/common', () => ({
  i18n_name: (value: string) => value,
}))

import AvatarIndex from '../../layout/layout-header/avatar/index.test-entry'
import ResetPassword from '../../layout/layout-header/avatar/ResetPassword.test-entry'
import { flushView, mountView } from '../helpers/view'

const ElDialogStub = defineComponent({
  name: 'ElDialogStub',
  props: {
    modelValue: {
      type: Boolean,
      default: false,
    },
    showClose: {
      type: Boolean,
      default: true,
    },
  },
  setup(props, { slots }) {
    return () =>
      h(
        'div',
        {
          'data-test': 'reset-password-dialog',
          'data-open': String(props.modelValue),
          'data-show-close': String(props.showClose),
        },
        [slots.default?.(), slots.footer?.()],
      )
  },
})

const ElFormStub = defineComponent({
  name: 'ElFormStub',
  setup(_, { slots, expose }) {
    expose({
      validate: vi.fn(() => Promise.resolve()),
      resetFields: vi.fn(),
    })

    return () => h('form', slots.default?.())
  },
})

const ElFormItemStub = defineComponent({
  name: 'ElFormItemStub',
  setup(_, { slots }) {
    return () => h('div', slots.default?.())
  },
})

const CurrentPasswordResetFormStub = defineComponent({
  name: 'CurrentPasswordResetFormStub',
  props: {
    forced: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['success', 'cancel'],
  setup(props, { emit, expose }) {
    expose({
      reset: vi.fn(),
    })

    return () =>
      h('div', { 'data-test': 'current-password-reset-form', 'data-forced': String(props.forced) }, [
        !props.forced
          ? h(
              'button',
              {
                type: 'button',
                onClick: () => emit('cancel'),
              },
              'common.cancel',
            )
          : null,
        h(
          'button',
              {
                type: 'button',
                onClick: () => {
                  mocks.resetCurrentPassword()
                  mocks.clearToken()
                  mocks.routerPush({ name: 'login' })
                  emit('success')
                },
          },
          'common.save',
        ),
      ])
  },
})

const ResetPasswordStub = defineComponent({
  name: 'ResetPasswordStub',
  props: {
    forced: {
      type: Boolean,
      default: false,
    },
  },
  setup(props, { expose }) {
    expose({
      open: vi.fn(),
      close: vi.fn(),
    })

    return () =>
      h('div', {
        'data-test': 'reset-password-stub',
        'data-forced': String(props.forced),
      })
  },
})

const DialogShellStub = defineComponent({
  name: 'DialogShellStub',
  setup(_, { expose }) {
    expose({
      open: vi.fn(),
    })

    return () => h('div')
  },
})

function mountResetPassword(props?: { forced?: boolean }) {
  return mountView(ResetPassword, {
    props,
    global: {
      stubs: {
        'el-dialog': ElDialogStub,
        'el-form': ElFormStub,
        'el-form-item': ElFormItemStub,
        CurrentPasswordResetForm: CurrentPasswordResetFormStub,
      },
    },
  })
}

describe('Reset password mandatory flow', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.userInfo.is_edit_password = false
  })

  it('passes forced mode to the avatar reset password entry when the profile requires it', async () => {
    mocks.userInfo.is_edit_password = true

    const wrapper = mountView(AvatarIndex, {
      global: {
        stubs: {
          ResetPassword: ResetPasswordStub,
          AboutDialog: DialogShellStub,
          APIKeyDialog: DialogShellStub,
          TagGroup: true,
          ArrowRight: true,
          Check: true,
        },
      },
    })

    await flushView()

    expect(wrapper.get('[data-test="reset-password-stub"]').attributes('data-forced')).toBe('true')
  })

  it('blocks normal dismissal controls in forced mode until save completes', async () => {
    const wrapper = mountResetPassword({ forced: true })
    const vm = wrapper.vm as unknown as { open: () => void; close: (force?: boolean) => void }

    vm.open()
    await flushView()

    expect(wrapper.get('[data-test="reset-password-dialog"]').attributes('data-show-close')).toBe(
      'false',
    )
    expect(wrapper.text()).not.toContain('common.cancel')

    vm.close()
    await flushView()

    expect(wrapper.get('[data-test="reset-password-dialog"]').attributes('data-open')).toBe('true')

    const saveButton = wrapper
      .findAll('button')
      .find((button) => button.text().trim() === 'common.save')

    expect(saveButton).toBeTruthy()

    await saveButton!.trigger('click')
    await flushView()

    expect(mocks.resetCurrentPassword).toHaveBeenCalledTimes(1)
    expect(mocks.clearToken).toHaveBeenCalledTimes(1)
    expect(mocks.routerPush).toHaveBeenCalledWith({ name: 'login' })
    expect(wrapper.get('[data-test="reset-password-dialog"]').attributes('data-open')).toBe('false')
  })

  it('remains dismissible when password hardening is not required', async () => {
    const wrapper = mountResetPassword({ forced: false })
    const vm = wrapper.vm as unknown as { open: () => void }

    vm.open()
    await flushView()

    expect(wrapper.get('[data-test="reset-password-dialog"]').attributes('data-show-close')).toBe(
      'true',
    )

    const cancelButton = wrapper
      .findAll('button')
      .find((button) => button.text().trim() === 'common.cancel')

    expect(cancelButton).toBeTruthy()

    await cancelButton!.trigger('click')
    await flushView()

    expect(wrapper.get('[data-test="reset-password-dialog"]').attributes('data-open')).toBe('false')
    expect(mocks.resetCurrentPassword).not.toHaveBeenCalled()
  })
})
