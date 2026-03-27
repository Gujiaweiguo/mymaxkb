import { describe, it, expect } from 'vitest'

function getChatOrigin(
  origin: string,
  prefix: string,
  chatPrefix: string,
  isDev: boolean,
): string {
  const currentOrigin = new URL(origin)
  const hasDedicatedChatPrefix = Boolean(chatPrefix && chatPrefix !== prefix)

  if (isDev && hasDedicatedChatPrefix && currentOrigin.port === '3000') {
    currentOrigin.port = '3001'
  }

  return currentOrigin.origin
}

function getChatBaseUrl(origin: string, prefix: string, chatPrefix: string, isDev: boolean): string {
  const chatOrigin = getChatOrigin(origin, prefix, chatPrefix, isDev)
  return `${chatOrigin}${chatPrefix ? chatPrefix : prefix}`
}

function getChatApiBaseUrl(origin: string, prefix: string, chatPrefix: string, isDev: boolean): string {
  return `${getChatBaseUrl(origin, prefix, chatPrefix, isDev)}/api`
}

describe('Chat URL helpers', () => {
  describe('getChatOrigin', () => {
    it('should rewrite to port 3001 in DEV when on 3000 with separate chat prefix', () => {
      expect(getChatOrigin('http://119.29.59.128:3000', '/admin', '/chat', true)).toBe(
        'http://119.29.59.128:3001',
      )
    })

    it('should keep original origin when not on port 3000 in DEV mode', () => {
      expect(getChatOrigin('http://119.29.59.128:3001', '/admin', '/chat', true)).toBe(
        'http://119.29.59.128:3001',
      )
    })

    it('should keep original origin in PROD mode', () => {
      expect(getChatOrigin('https://example.com', '/admin', '/chat', false)).toBe('https://example.com')
    })

    it('should keep original origin when prefixes are the same', () => {
      expect(getChatOrigin('http://localhost:3000', '/admin', '/admin', true)).toBe(
        'http://localhost:3000',
      )
    })

    it('should keep original origin when chatPrefix is empty', () => {
      expect(getChatOrigin('http://localhost:3000', '/admin', '', true)).toBe('http://localhost:3000')
    })
  })

  describe('getChatBaseUrl', () => {
    it('should return chat prefix appended to chat origin', () => {
      expect(getChatBaseUrl('https://example.com', '/admin', '/chat', false)).toBe(
        'https://example.com/chat',
      )
    })

    it('should fall back to prefix when chatPrefix is empty', () => {
      expect(getChatBaseUrl('https://example.com', '/admin', '', false)).toBe('https://example.com/admin')
    })

    it('should use rewritten origin in DEV on port 3000 with separate prefixes', () => {
      expect(getChatBaseUrl('http://119.29.59.128:3000', '/admin', '/chat', true)).toBe(
        'http://119.29.59.128:3001/chat',
      )
    })
  })

  describe('getChatApiBaseUrl', () => {
    it('should append /api to the chat base URL', () => {
      expect(getChatApiBaseUrl('https://example.com', '/admin', '/chat', false)).toBe(
        'https://example.com/chat/api',
      )
    })

    it('should use rewritten origin in DEV on port 3000 with separate prefixes', () => {
      expect(getChatApiBaseUrl('http://119.29.59.128:3000', '/admin', '/chat', true)).toBe(
        'http://119.29.59.128:3001/chat/api',
      )
    })
  })
})
