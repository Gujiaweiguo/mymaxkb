import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import useApplicationStore from '@/stores/modules/application'

describe('Application Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should initialize with location property derived from window globals', () => {
    const store = useApplicationStore()
    expect(typeof store.location).toBe('string')
    expect(store.location).toMatch(/^https?:\/\/.+\//)
  })
})
