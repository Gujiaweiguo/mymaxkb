import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  route: { path: '/knowledge', params: {}, query: {} },
  permissionMap: {
    knowledge: {
      workspace: {
        is_share: vi.fn(() => true),
      },
      systemShare: {
        is_share: vi.fn(() => true),
      },
      systemManage: {
        is_share: vi.fn(() => true),
      },
    },
  },
}))

vi.mock('vue-router', async (importOriginal) => {
  const actual = await importOriginal<typeof import('vue-router')>()

  return {
    ...actual,
    useRoute: () => mocks.route,
  }
})

vi.mock('@/permission', () => ({
  default: mocks.permissionMap,
}))

vi.mock('@/views/knowledge/component/KnowledgeListContainer.vue', () => ({
  default: {
    name: 'KnowledgeListContainer',
    template: '<div><slot name="header" /><slot /></div>',
  },
}))

import useStore from '../../stores'
import { SourceTypeEnum } from '../../enums/common'
import KnowledgeManageView from '../../views/knowledge/index.vue'
import { activateTestPinia, flushView, mountView } from '../helpers/view'

describe('Knowledge Management View', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.route.path = '/knowledge'
    activateTestPinia()

    const { folder } = useStore()
    folder.currentFolder = {}
    vi.spyOn(folder, 'asyncGetFolder').mockResolvedValue({
      data: [
        { id: 'default', name: 'All knowledge' },
        { id: 'team', name: 'Team knowledge' },
      ],
    })
  })

  it('loads workspace folders on mount and selects the first folder by default', async () => {
    const wrapper = mountView(KnowledgeManageView)

    await flushView()

    const { folder } = useStore()

    expect(folder.asyncGetFolder).toHaveBeenCalledWith(
      SourceTypeEnum.KNOWLEDGE,
      {},
      'workspace',
      expect.any(Object),
    )
    expect(folder.currentFolder.id).toBe('default')
    expect(wrapper.find('[data-test="knowledge-list-container"]').exists()).toBe(true)
  })

  it('uses the shared knowledge API mode when the route is shared', async () => {
    mocks.route.path = '/knowledge/shared/list'

    const { folder } = useStore()
    folder.currentFolder = {}
    vi.spyOn(folder, 'asyncGetFolder').mockResolvedValue({
      data: [
        { id: 'share', name: 'Shared knowledge' },
        { id: 'team', name: 'Team knowledge' },
      ],
    })

    const wrapper = mountView(KnowledgeManageView)

    await flushView()

    expect(folder.asyncGetFolder).toHaveBeenCalledWith(
      SourceTypeEnum.KNOWLEDGE,
      {},
      'systemShare',
      expect.any(Object),
    )
    expect(wrapper.text()).toContain('views.shared.shared_knowledge')
  })

  it('clears the knowledge list when switching folders', async () => {
    const { knowledge } = useStore()
    const setKnowledgeListSpy = vi.spyOn(knowledge, 'setKnowledgeList')
    const wrapper = mountView(KnowledgeManageView)

    await flushView()
    await wrapper.get('[data-test="folder-node-team"]').trigger('click')

    expect(setKnowledgeListSpy).toHaveBeenCalledWith([])
    expect(useStore().folder.currentFolder.id).toBe('team')
  })
})
