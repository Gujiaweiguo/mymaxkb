import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}))

vi.mock('@/request/index', () => ({
  get: mocks.get,
  post: mocks.post,
}))

import LoginApi from '@/api/user/login'

describe('User API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('calls the login endpoint through the shared request client', async () => {
    mocks.post.mockResolvedValue({ data: { token: 'test-token' } })

    const payload = {
      username: 'testuser',
      password: 'password123',
      login_type: 'LOCAL',
    }

    const result = await LoginApi.login(payload)

    expect(mocks.post).toHaveBeenCalledWith('/user/login', payload, undefined, undefined)
    expect(result.data.token).toBe('test-token')
  })

  it('calls the logout endpoint through the shared request client', async () => {
    mocks.post.mockResolvedValue({ data: true })

    await LoginApi.logout()

    expect(mocks.post).toHaveBeenCalledWith('/user/logout', undefined, undefined, undefined)
  })

  it('requests user captcha with the username query parameter', async () => {
    mocks.get.mockResolvedValue({ data: { captcha_svg: '<svg />' } })

    const result = await LoginApi.getCaptcha('testuser')

    expect(mocks.get).toHaveBeenCalledWith('/user/captcha', { username: 'testuser' }, undefined)
    expect(result.data.captcha_svg).toBe('<svg />')
  })
})
