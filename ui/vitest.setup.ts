import { config } from '@vue/test-utils'
import { vi as vitestVi } from 'vitest'

config.global.renderStubDefaultSlot = true

Object.defineProperty(window, 'MaxKB', {
  writable: true,
  configurable: true,
  value: {
    chatPrefix: '/chat',
    prefix: '/admin',
  },
})

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

class ResizeObserver {
  observe() {}

  unobserve() {}

  disconnect() {}
}

class IntersectionObserver {
  root = null

  rootMargin = ''

  thresholds = []

  observe() {}

  unobserve() {}

  disconnect() {}

  takeRecords() {
    return []
  }
}

Object.defineProperty(window, 'ResizeObserver', {
  writable: true,
  configurable: true,
  value: ResizeObserver,
})

Object.defineProperty(window, 'IntersectionObserver', {
  writable: true,
  configurable: true,
  value: IntersectionObserver,
})

Element.prototype.scrollIntoView = vitestVi.fn()
