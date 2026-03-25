import { beforeAll, afterAll, afterEach, vi, expect } from 'vitest'
import { config } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { vi as vitestVi } from 'vitest'

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vitestVi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vitestVi.fn(),
    removeListener: vitestVi.fn(),
    dispatchEvent: vitestVi.fn(),
  })),
})

// Global test utilities
export const createWrapper = (component: any, options: any = {}) => {
  const pinia = createPinia()
  setActivePinia(pinia)

  return config(component, {
    global: {
      plugins: [pinia],
    },
    ...options,
  })
}
