import { beforeEach, describe, expect, it, vi } from 'vitest'
import { defineComponent, h } from 'vue'

const mocks = vi.hoisted(() => ({
  routerPush: vi.fn(),
  clearToken: vi.fn(),
  resetCurrentPassword: vi.fn(() => Promise.resolve()),
}))

vi.mock('vue-router', async (importOriginal) => {
  const actual = await importOriginal<typeof import('vue-router')>()

  return {
    ...actual,
    useRouter: () => ({
      push: mocks.routerPush,
    }),
  }
})

vi.mock('@/stores', () => ({
  default: () => ({
    login: {
      clearToken: mocks.clearToken,
    },
  }),
}))

vi.mock('@/api/user/user', () => ({
  default: {
    resetCurrentPassword: mocks.resetCurrentPassword,
  },
}))

vi.mock('@/locales', () => ({
  t: (key: string) => key,
}))

import CurrentPasswordResetForm from '../../components/user/CurrentPasswordResetForm.vue'
import { flushView, mountView } from '../helpers/view'

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

describe('CurrentPasswordResetForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('clears the local token and redirects to login after a successful password reset', async () => {
    const wrapper = mountView(CurrentPasswordResetForm, {
      props: {
        forced: true,
      },
      global: {
        stubs: {
          'el-form': ElFormStub,
          'el-form-item': ElFormItemStub,
        },
      },
    })

    const saveButton = wrapper
      .findAll('button')
      .find((button) => button.text().trim() === 'common.save')

    expect(saveButton).toBeTruthy()

    await saveButton!.trigger('click')
    await flushView()

    expect(mocks.resetCurrentPassword).toHaveBeenCalledTimes(1)
    expect(mocks.clearToken).toHaveBeenCalledTimes(1)
    expect(mocks.routerPush).toHaveBeenCalledWith({ name: 'login' })
  })
})
