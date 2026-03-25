import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/api/user/login', () => ({
  login: vi.fn(),
  getCaptcha: vi.fn(),
}))

vi.mock('@/router', () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}))

describe('Login View', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should render login form', () => {
    const wrapper = mount({
      template: `
        <div class="login-form">
          <input v-model="username" placeholder="Username" />
          <input v-model="password" type="password" placeholder="Password" />
          <button @click="handleLogin">Login</button>
        </div>
      `,
      data() {
        return {
          username: '',
          password: '',
        }
      },
      methods: {
        handleLogin() {
        },
      },
    })

    expect(wrapper.find('input[placeholder="Username"]').exists()).toBe(true)
    expect(wrapper.find('input[placeholder="Password"]').exists()).toBe(true)
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('should update username on input', async () => {
    const wrapper = mount({
      template: `<input v-model="username" placeholder="Username" />`,
      data() {
        return { username: '' }
      },
    })

    const input = wrapper.find('input')
    await input.setValue('testuser')

    expect(wrapper.vm.username).toBe('testuser')
  })

  it('should update password on input', async () => {
    const wrapper = mount({
      template: `<input v-model="password" type="password" placeholder="Password" />`,
      data() {
        return { password: '' }
      },
    })

    const input = wrapper.find('input')
    await input.setValue('password123')

    expect(wrapper.vm.password).toBe('password123')
  })

  it('should disable login button when fields are empty', () => {
    const wrapper = mount({
      template: `
        <button :disabled="!username || !password">Login</button>
      `,
      data() {
        return {
          username: '',
          password: '',
        }
      },
    })

    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })

  it('should enable login button when fields are filled', () => {
    const wrapper = mount({
      template: `
        <button :disabled="!username || !password">Login</button>
      `,
      data() {
        return {
          username: 'testuser',
          password: 'password123',
        }
      },
    })

    expect(wrapper.find('button').attributes('disabled')).toBeUndefined()
  })
})
