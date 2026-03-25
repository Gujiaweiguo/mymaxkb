import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useApplicationStore } from '@/stores/modules/application'

vi.mock('@/api/application', () => ({
  getApplicationList: vi.fn(),
  getApplicationDetail: vi.fn(),
  createApplication: vi.fn(),
  updateApplication: vi.fn(),
  deleteApplication: vi.fn(),
}))

describe('Application Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should initialize with default state', () => {
    const store = useApplicationStore()

    expect(store.applicationList).toEqual([])
    expect(store.currentApplication).toBeNull()
  })

  it('should set application list correctly', () => {
    const store = useApplicationStore()
    const mockApps = [
      { id: '1', name: 'App 1', desc: 'Description 1' },
      { id: '2', name: 'App 2', desc: 'Description 2' },
    ]

    store.setApplicationList(mockApps)

    expect(store.applicationList).toEqual(mockApps)
  })

  it('should set current application correctly', () => {
    const store = useApplicationStore()
    const mockApp = { id: '1', name: 'Test App', desc: 'Test Description' }

    store.setCurrentApplication(mockApp)

    expect(store.currentApplication).toEqual(mockApp)
  })

  it('should clear current application', () => {
    const store = useApplicationStore()
    const mockApp = { id: '1', name: 'Test App', desc: 'Test Description' }

    store.setCurrentApplication(mockApp)
    store.clearCurrentApplication()

    expect(store.currentApplication).toBeNull()
  })
})
