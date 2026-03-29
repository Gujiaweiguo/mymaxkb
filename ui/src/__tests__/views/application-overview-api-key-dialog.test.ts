import { beforeEach, describe, expect, it, vi } from 'vitest'
import { computed, defineComponent, h, inject, provide, ref, type Ref } from 'vue'

const mocks = vi.hoisted(() => ({
  route: {
    path: '/application/workspace/app-1/overview',
    params: { id: 'app-1' },
  },
  getAPIKey: vi.fn(),
  postAPIKey: vi.fn(() => Promise.resolve()),
  putAPIKey: vi.fn(() => Promise.resolve()),
  delAPIKey: vi.fn(() => Promise.resolve()),
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
    getAPIKey: mocks.getAPIKey,
    postAPIKey: mocks.postAPIKey,
    putAPIKey: mocks.putAPIKey,
    delAPIKey: mocks.delAPIKey,
  })),
}))

vi.mock('@/utils/time', () => ({
  datetimeFormat: vi.fn((value: string) => value),
  fromNowDate: vi.fn(() => ''),
}))

vi.mock('@/utils/message', () => ({
  MsgSuccess: mocks.MsgSuccess,
  MsgConfirm: mocks.MsgConfirm,
}))

vi.mock('@/locales', () => ({
  t: (key: string) => key,
}))

vi.mock('@/views/application-overview/component/SettingAPIKeyDrawer.vue', () => ({
  default: {
    name: 'SettingAPIKeyDrawerStub',
    methods: {
      open() {},
    },
    render() {
      return null
    },
  },
}))

import ApplicationApiKeyDialog from '../../views/application-overview/component/APIKeyDialog.vue'
import { flushView, mountView } from '../helpers/view'

const TableRowsKey = Symbol('tableRows')

const ElDialogStub = defineComponent({
  name: 'ElDialogStub',
  props: {
    modelValue: {
      type: Boolean,
      default: false,
    },
  },
  setup(props, { slots }) {
    return () =>
      h(
        'div',
        {
          'data-test': 'api-key-dialog',
          'data-open': String(props.modelValue),
        },
        slots.default?.(),
      )
  },
})

const AppTableStub = defineComponent({
  name: 'AppTableStub',
  props: {
    data: {
      type: Array,
      default: () => [],
    },
  },
  setup(props, { slots }) {
    provide(TableRowsKey, computed(() => (props.data as Array<Record<string, any>>) ?? []))

    return () => h('div', { 'data-test': 'app-table' }, slots.default?.())
  },
})

const ElTableColumnStub = defineComponent({
  name: 'ElTableColumnStub',
  props: {
    prop: {
      type: String,
      default: '',
    },
    label: {
      type: String,
      default: '',
    },
  },
  setup(props, { slots }) {
    const rows = inject<Ref<Array<Record<string, any>>>>(TableRowsKey, ref([]))

    return () =>
      h(
        'div',
        { 'data-test': `column-${props.prop || props.label || 'default'}` },
        rows.value.map((row, index) =>
          h(
            'div',
            {
              'data-test': `column-row-${index}`,
            },
            slots.default?.({ row }) ?? row[props.prop],
          ),
        ),
      )
  },
})

const AppIconStub = defineComponent({
  name: 'AppIconStub',
  props: {
    iconName: {
      type: String,
      default: '',
    },
  },
  setup(props) {
    return () => h('span', { 'data-test': 'app-icon', 'data-icon-name': props.iconName })
  },
})

function mountDialog() {
  return mountView(ApplicationApiKeyDialog, {
    global: {
      stubs: {
        'el-dialog': ElDialogStub,
        'app-table': AppTableStub,
        'el-table-column': ElTableColumnStub,
        AppIcon: AppIconStub,
      },
    },
  })
}

function openDialog(wrapper: ReturnType<typeof mountDialog>) {
  ;(wrapper.vm as unknown as { open: () => void }).open()
}

function getCopyButtons(wrapper: ReturnType<typeof mountDialog>) {
  return wrapper.findAll('button').filter((button) => button.find('[data-icon-name="app-copy"]').exists())
}

describe('Application overview API key dialog', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders masked listed keys without a copy action', async () => {
    mocks.getAPIKey.mockResolvedValue({
      data: {
        records: [
          {
            id: 'key-1',
            secret_key: 'sk-app-****-masked',
            is_active: true,
            allow_cross_domain: false,
            is_permanent: true,
            expire_time: '',
            create_time: '2026-03-29 10:00:00',
          },
        ],
        total: 1,
      },
    })

    const wrapper = mountDialog()
    openDialog(wrapper)
    await flushView()

    expect(wrapper.text()).toContain('sk-app-****-masked')
    expect(getCopyButtons(wrapper)).toHaveLength(0)
  })

  it('keeps copy enabled for unmasked listed keys', async () => {
    mocks.getAPIKey.mockResolvedValue({
      data: {
        records: [
          {
            id: 'key-2',
            secret_key: 'sk-app-live-secret',
            is_active: true,
            allow_cross_domain: false,
            is_permanent: true,
            expire_time: '',
            create_time: '2026-03-29 10:00:00',
          },
        ],
        total: 1,
      },
    })

    const wrapper = mountDialog()
    openDialog(wrapper)
    await flushView()

    const [copyButton] = getCopyButtons(wrapper)

    expect(copyButton).toBeTruthy()

    await copyButton.trigger('click')

    expect(mocks.copyClick).toHaveBeenCalledWith('sk-app-live-secret')
  })
})
