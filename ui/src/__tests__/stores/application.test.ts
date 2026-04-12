import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

describe('Application Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('uses the dedicated chat prefix when it is configured', async () => {
    vi.resetModules()
    window.MaxKB = {
      prefix: '/admin',
      chatPrefix: '/chat',
    } as typeof window.MaxKB

    const { default: useApplicationStore } = await import('@/stores/modules/application')
    const store = useApplicationStore()

    expect(store.location).toBe('http://localhost:3001/chat/')
  })

  it('falls back to the admin prefix when chat prefix is empty', async () => {
    vi.resetModules()
    window.MaxKB = {
      prefix: '/admin',
      chatPrefix: '',
    } as typeof window.MaxKB

    const { default: useApplicationStore } = await import('@/stores/modules/application')
    const store = useApplicationStore()

    expect(store.location).toBe(`${window.location.origin}/admin/`)
  })
})
