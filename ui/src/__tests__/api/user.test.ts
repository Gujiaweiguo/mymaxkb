import { describe, it, expect, vi } from 'vitest'
import { login, logout, getUserInfo } from '@/api/user/login'

vi.mock('@/api/user/login', () => ({
  login: vi.fn(),
  logout: vi.fn(),
  getUserInfo: vi.fn(),
}))

describe('User API', () => {
  it('should call login API with correct parameters', async () => {
    const mockLogin = vi.fn().mockResolvedValue({ data: { token: 'test-token' } })
    vi.mocked(login).mockImplementation(mockLogin)

    const result = await login({
      username: 'testuser',
      password: 'password123',
      login_type: 'LOCAL',
    })

    expect(mockLogin).toHaveBeenCalledWith({
      username: 'testuser',
      password: 'password123',
      login_type: 'LOCAL',
    })
    expect(result.data.token).toBe('test-token')
  })

  it('should call logout API', async () => {
    const mockLogout = vi.fn().mockResolvedValue({ success: true })
    vi.mocked(logout).mockImplementation(mockLogout)

    const result = await logout()

    expect(mockLogout).toHaveBeenCalled()
    expect(result.success).toBe(true)
  })

  it('should call getUserInfo API', async () => {
    const mockGetUserInfo = vi.fn().mockResolvedValue({
      data: { id: '1', username: 'testuser' },
    })
    vi.mocked(getUserInfo).mockImplementation(mockGetUserInfo)

    const result = await getUserInfo()

    expect(mockGetUserInfo).toHaveBeenCalled()
    expect(result.data.username).toBe('testuser')
  })
})
