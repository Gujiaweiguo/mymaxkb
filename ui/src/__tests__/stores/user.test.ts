import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '@/stores/modules/user'

vi.mock('@/api/user/login', () => ({
  login: vi.fn(),
  logout: vi.fn(),
  getUserInfo: vi.fn(),
}))

describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should initialize with default state', () => {
    const store = useUserStore()

    expect(store.user).toBeNull()
    expect(store.token).toBe('')
  })

  it('should set user correctly', () => {
    const store = useUserStore()
    const mockUser = {
      id: '1',
      username: 'testuser',
      email: 'test@example.com',
      role: 'USER',
    }

    store.setUser(mockUser)

    expect(store.user).toEqual(mockUser)
  })

  it('should set token correctly', () => {
    const store = useUserStore()

    store.setToken('test-token')

    expect(store.token).toBe('test-token')
  })

  it('should clear user on logout', () => {
    const store = useUserStore()
    const mockUser = {
      id: '1',
      username: 'testuser',
      email: 'test@example.com',
      role: 'USER',
    }

    store.setUser(mockUser)
    store.setToken('test-token')
    store.clearUser()

    expect(store.user).toBeNull()
    expect(store.token).toBe('')
  })
})
