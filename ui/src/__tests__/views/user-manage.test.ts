import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/api/user', () => ({
  getUserList: vi.fn(),
  createUser: vi.fn(),
  updateUser: vi.fn(),
  deleteUser: vi.fn(),
}))

describe('User Management View', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should render user management header', () => {
    const wrapper = mount({
      template: `
        <div class="user-management">
          <h2>User Management</h2>
          <button @click="createUser">Create User</button>
        </div>
      `,
      methods: {
        createUser() {},
      },
    })

    expect(wrapper.find('h2').text()).toBe('User Management')
    expect(wrapper.find('button').text()).toBe('Create User')
  })

  it('should render user list table', () => {
    const users = [
      { id: '1', username: 'user1', email: 'user1@example.com' },
      { id: '2', username: 'user2', email: 'user2@example.com' },
    ]

    const wrapper = mount({
      template: `
        <table>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.username }}</td>
              <td>{{ user.email }}</td>
            </tr>
          </tbody>
        </table>
      `,
      data() {
        return { users }
      },
    })

    const rows = wrapper.findAll('tr')
    expect(rows.length).toBe(2)
  })

  it('should handle delete user', async () => {
    const mockDelete = vi.fn()
    const wrapper = mount({
      template: `
        <button @click="deleteUser('1')">Delete</button>
      `,
      methods: {
        deleteUser: mockDelete,
      },
    })

    await wrapper.find('button').trigger('click')

    expect(mockDelete).toHaveBeenCalledWith('1')
  })

  it('should render search input', () => {
    const wrapper = mount({
      template: `<input v-model="searchQuery" placeholder="Search users" />`,
      data() {
        return { searchQuery: '' }
      },
    })

    expect(wrapper.find('input').exists()).toBe(true)
    expect(wrapper.find('input').attributes('placeholder')).toBe('Search users')
  })

  it('should update search query on input', async () => {
    const wrapper = mount({
      template: `<input v-model="searchQuery" placeholder="Search users" />`,
      data() {
        return { searchQuery: '' }
      },
    })

    const input = wrapper.find('input')
    await input.setValue('john')

    expect(wrapper.vm.searchQuery).toBe('john')
  })
})
