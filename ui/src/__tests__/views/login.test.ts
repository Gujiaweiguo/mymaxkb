import { beforeEach, describe, expect, it, vi } from 'vitest'
import { defineComponent, h } from 'vue'

const mocks = vi.hoisted(() => ({
  route: {
    query: {},
    fullPath: '/login',
  },
  routerPush: vi.fn(),
  getLoginAuthSetting: vi.fn(),
  getLoginViewAuthSetting: vi.fn(),
  getCaptcha: vi.fn(),
  samlLogin: vi.fn(),
  asyncGetProfile: vi.fn(),
  asyncLogin: vi.fn(),
  asyncLdapLogin: vi.fn(),
  dingOauth2Callback: vi.fn(),
  wecomCallback: vi.fn(),
  larkCallback: vi.fn(),
}))

vi.mock('vue-router', async (importOriginal) => {
  const actual = await importOriginal<typeof import('vue-router')>()

  return {
    ...actual,
    useRouter: () => ({
      push: mocks.routerPush,
    }),
    useRoute: () => mocks.route,
  }
})

vi.mock('@/stores', () => ({
  default: () => ({
    login: {
      asyncLogin: mocks.asyncLogin,
      asyncLdapLogin: mocks.asyncLdapLogin,
      dingOauth2Callback: mocks.dingOauth2Callback,
      wecomCallback: mocks.wecomCallback,
      larkCallback: mocks.larkCallback,
    },
    user: {
      asyncGetProfile: mocks.asyncGetProfile,
      rasKey: 'test-public-key',
    },
    theme: {
      themeInfo: {
        theme: '#409eff',
        slogan: '',
      },
    },
  }),
}))

vi.mock('@/api/system-settings/auth-setting', () => ({
  default: {
    getLoginAuthSetting: mocks.getLoginAuthSetting,
    getLoginViewAuthSetting: mocks.getLoginViewAuthSetting,
  },
}))

vi.mock('@/api/user/login', () => ({
  default: {
    getCaptcha: mocks.getCaptcha,
    samlLogin: mocks.samlLogin,
  },
}))

vi.mock('@/locales', () => ({
  getBrowserLang: vi.fn(() => 'en-US'),
  t: (key: string) => key,
}))

vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    locale: {
      value: 'en-US',
    },
  }),
}))

vi.mock('@/utils/message.ts', () => ({
  MsgConfirm: vi.fn(() => Promise.resolve()),
  MsgError: vi.fn(),
}))

vi.mock('@/utils/common', () => ({
  loadScript: vi.fn(() => Promise.resolve()),
}))

vi.mock('dingtalk-jsapi', () => ({
  runtime: {
    permission: {
      requestAuthCode: vi.fn(() => Promise.resolve({ code: 'auth-code' })),
    },
  },
}))

vi.mock('node-forge', () => ({
  default: {
    pki: {
      publicKeyFromPem: vi.fn(() => ({
        encrypt: vi.fn(() => 'encrypted'),
      })),
    },
    util: {
      encodeUtf8: vi.fn((value: string) => value),
      encode64: vi.fn(() => 'encoded'),
    },
  },
}))

import LoginView from '../../views/login/index.vue'
import { flushView, mountView } from '../helpers/view'

const createSlotStub = (name: string) =>
  defineComponent({
    name,
    props: {
      subTitle: {
        type: String,
        default: '',
      },
      tabs: {
        type: Array,
        default: () => [],
      },
      defaultTab: {
        type: String,
        default: '',
      },
    },
    setup(_, { slots }) {
      return () => h('div', { 'data-test': name }, slots.default?.())
    },
  })

const ElFormStub = defineComponent({
  name: 'ElFormStub',
  setup(_, { slots, expose }) {
    expose({
      validate: (callback: (valid: boolean) => void) => callback(true),
      clearValidate: vi.fn(),
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

async function mountLogin(loginAuthSetting: { default_value: string; login_methods: string[]; max_attempts?: number }) {
  mocks.getLoginAuthSetting.mockResolvedValue({
    data: loginAuthSetting,
  })

  const wrapper = mountView(LoginView, {
    global: {
      stubs: {
        LoginLayout: createSlotStub('login-layout'),
        LoginContainer: createSlotStub('login-container'),
        QrCodeTab: createSlotStub('qr-code-tab'),
        'el-form': ElFormStub,
        'el-form-item': ElFormItemStub,
      },
    },
  })

  await flushView()
  await flushView()

  return wrapper
}

function methodTexts(wrapper: ReturnType<typeof mountView>) {
  return wrapper
    .findAll('button')
    .map((button: { text: () => string }) => button.text().trim())
    .filter(Boolean)
}

describe('Login View', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.route.query = {}
    mocks.route.fullPath = '/login'
    mocks.asyncGetProfile.mockResolvedValue({})
    mocks.getLoginViewAuthSetting.mockResolvedValue({ data: null })
    mocks.getCaptcha.mockResolvedValue({ data: { captcha: '' } })
    mocks.samlLogin.mockResolvedValue({ data: '' })
  })

  it('shows the local username/password form without extra sign-in method buttons when only LOCAL is enabled', async () => {
    const wrapper = await mountLogin({
      default_value: 'LOCAL',
      login_methods: ['LOCAL'],
      max_attempts: -1,
    })

    expect(
      wrapper.find('input[placeholder="views.login.loginForm.username.placeholder"]').exists(),
    ).toBe(true)
    expect(
      wrapper.find('input[placeholder="views.login.loginForm.password.placeholder"]').exists(),
    ).toBe(true)
    expect(wrapper.text()).not.toContain('views.login.moreMethod')
    expect(methodTexts(wrapper)).not.toContain('LDAP')
    expect(methodTexts(wrapper)).not.toContain('CAS')
  })

  it('shows LDAP in the method switcher when LDAP is enabled alongside LOCAL', async () => {
    const wrapper = await mountLogin({
      default_value: 'LOCAL',
      login_methods: ['LOCAL', 'LDAP'],
      max_attempts: -1,
    })

    expect(wrapper.text()).toContain('views.login.moreMethod')
    expect(methodTexts(wrapper)).toContain('LDAP')
  })

  it('omits disabled sign-in methods from the rendered method switcher', async () => {
    const wrapper = await mountLogin({
      default_value: 'LOCAL',
      login_methods: ['LOCAL', 'LDAP'],
      max_attempts: -1,
    })

    const methods = methodTexts(wrapper)

    expect(methods).not.toContain('CAS')
    expect(methods).not.toContain('OIDC')
    expect(methods).not.toContain('SAML2')
  })
})
