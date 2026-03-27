import { shallowMount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { defineComponent, h, nextTick } from 'vue'

const translate = (key: string) => key

const createSlotStub = (name: string, slotNames: string[] = ['default']) =>
  defineComponent({
    name: `${name}Stub`,
    setup(_, { slots }) {
      return () =>
        h(
          'div',
          { 'data-test': name },
          slotNames.flatMap((slotName) => slots[slotName]?.() ?? []),
        )
    },
  })

const ClickableStub = defineComponent({
  name: 'ClickableStub',
  emits: ['click'],
  setup(_, { slots, emit }) {
    return () =>
      h(
        'button',
        {
          type: 'button',
          onClick: (event) => emit('click', event),
        },
        slots.default?.(),
      )
  },
})

const ElInputStub = defineComponent({
  name: 'ElInputStub',
  props: {
    modelValue: {
      type: String,
      default: '',
    },
    placeholder: {
      type: String,
      default: '',
    },
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { emit }) {
    return () =>
      h('input', {
        value: props.modelValue,
        placeholder: props.placeholder,
        onInput: (event) => {
          const value = (event.target as HTMLInputElement).value
          emit('update:modelValue', value)
        },
        onChange: (event) => {
          const value = (event.target as HTMLInputElement).value
          emit('change', value)
        },
      })
  },
})

const ElOptionStub = defineComponent({
  name: 'ElOptionStub',
  props: {
    value: {
      type: [String, Number, Boolean],
      default: '',
    },
    label: {
      type: String,
      default: '',
    },
  },
  setup(props, { slots }) {
    return () => h('option', { value: String(props.value ?? '') }, slots.default?.() ?? props.label)
  },
})

const ElSelectStub = defineComponent({
  name: 'ElSelectStub',
  props: {
    modelValue: {
      type: [String, Number, Boolean],
      default: '',
    },
  },
  emits: ['update:modelValue', 'change'],
  setup(props, { slots, emit }) {
    return () =>
      h(
        'select',
        {
          value: String(props.modelValue ?? ''),
          onChange: (event) => {
            const value = (event.target as HTMLSelectElement).value
            emit('update:modelValue', value)
            emit('change', value)
          },
        },
        slots.default?.(),
      )
  },
})

const FolderTreeStub = defineComponent({
  name: 'FolderTreeStub',
  props: {
    data: {
      type: Array,
      default: () => [],
    },
  },
  emits: ['handleNodeClick', 'refreshTree'],
  setup(props, { emit }) {
    return () =>
      h('div', { 'data-test': 'folder-tree' }, [
        ...(props.data as Array<Record<string, string>>).map((row) =>
          h(
            'button',
            {
              type: 'button',
              'data-test': `folder-node-${row.id}`,
              onClick: () => emit('handleNodeClick', row),
            },
            row.name,
          ),
        ),
        h(
          'button',
          {
            type: 'button',
            'data-test': 'folder-refresh',
            onClick: () => emit('refreshTree'),
          },
          'refresh',
        ),
      ])
  },
})

const CommonListStub = defineComponent({
  name: 'CommonListStub',
  props: {
    data: {
      type: Array,
      default: () => [],
    },
  },
  emits: ['click', 'mouseenter', 'mouseleave'],
  setup(props, { slots, emit }) {
    return () =>
      h(
        'div',
        { 'data-test': 'common-list' },
        (props.data as Array<Record<string, string>>).map((row) =>
          h(
            'button',
            {
              type: 'button',
              'data-test': `common-list-item-${row.id}`,
              onClick: () => emit('click', row),
              onMouseenter: () => emit('mouseenter', row),
              onMouseleave: () => emit('mouseleave', row),
            },
            slots.default?.({ row }) ?? row.name,
          ),
        ),
      )
  },
})

const CardBoxStub = defineComponent({
  name: 'CardBoxStub',
  props: {
    title: {
      type: String,
      default: '',
    },
    description: {
      type: String,
      default: '',
    },
  },
  emits: ['click'],
  setup(props, { slots, emit }) {
    return () =>
      h(
        'button',
        {
          type: 'button',
          'data-test': 'card-box',
          'data-title': props.title,
          onClick: (event) => emit('click', event),
        },
        [
          h('span', props.title),
          h('span', props.description),
          slots.icon?.(),
          slots.subTitle?.(),
          slots.tag?.(),
          slots.footer?.(),
          slots.mouseEnter?.(),
          slots.default?.(),
        ],
      )
  },
})

const EmptyStub = defineComponent({
  name: 'EmptyStub',
  props: {
    description: {
      type: String,
      default: '',
    },
  },
  setup(props) {
    return () => h('div', { 'data-test': 'empty-state' }, props.description)
  },
})

const defaultGlobal = {
  mocks: {
    $t: translate,
  },
  directives: {
    loading: {},
    hasPermission: {},
  },
  stubs: {
    LayoutContainer: createSlotStub('layout-container', ['left', 'default']),
    ContentContainer: createSlotStub('content-container', ['header', 'search', 'default']),
    KnowledgeListContainer: createSlotStub('knowledge-list-container', ['header', 'default']),
    FolderBreadcrumb: createSlotStub('folder-breadcrumb'),
    InfiniteScroll: createSlotStub('infinite-scroll'),
    AppIcon: createSlotStub('app-icon'),
    'folder-tree': FolderTreeStub,
    'common-list': CommonListStub,
    CardBox: CardBoxStub,
    'el-input': ElInputStub,
    'el-select': ElSelectStub,
    'el-option': ElOptionStub,
    'el-button': ClickableStub,
    'el-dropdown-item': ClickableStub,
    'el-card': createSlotStub('el-card'),
    'el-scrollbar': createSlotStub('el-scrollbar'),
    'el-dropdown': createSlotStub('el-dropdown', ['default', 'dropdown']),
    'el-dropdown-menu': createSlotStub('el-dropdown-menu'),
    'el-tooltip': createSlotStub('el-tooltip', ['default']),
    'el-upload': createSlotStub('el-upload', ['default']),
    'el-avatar': createSlotStub('el-avatar'),
    'el-tag': createSlotStub('el-tag'),
    'el-text': createSlotStub('el-text'),
    'el-divider': true,
    'el-icon': createSlotStub('el-icon'),
    'el-row': createSlotStub('el-row'),
    'el-col': createSlotStub('el-col'),
    'el-empty': EmptyStub,
    ArrowDown: true,
    'arrow-down': true,
    SuccessFilled: true,
    UserFilled: true,
    Search: true,
  },
}

type MountComponent = Parameters<typeof shallowMount>[0]
type MountOptions<T extends MountComponent> = NonNullable<Parameters<typeof shallowMount<T>>[1]>

export function activateTestPinia() {
  const pinia = createPinia()
  setActivePinia(pinia)
  return pinia
}

export function mountView<T extends MountComponent>(component: T, options?: MountOptions<T>) {
  const globalOptions = options?.global

  return shallowMount(component, {
    ...options,
    global: {
      ...defaultGlobal,
      ...globalOptions,
      mocks: {
        ...defaultGlobal.mocks,
        ...globalOptions?.mocks,
      },
      directives: {
        ...defaultGlobal.directives,
        ...globalOptions?.directives,
      },
      stubs: {
        ...defaultGlobal.stubs,
        ...globalOptions?.stubs,
      },
    },
  })
}

export async function flushView() {
  await flushPromises()
  await nextTick()
}
