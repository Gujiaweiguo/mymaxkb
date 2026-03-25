import { describe, it, expect, vi } from 'vitest'

describe('Utility Functions', () => {
  describe('formatDate', () => {
    it('should format date correctly', () => {
      const date = new Date('2024-01-15T10:30:00')
      const formatted = date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })

      expect(formatted).toContain('2024')
      expect(formatted).toContain('Jan')
      expect(formatted).toContain('15')
    })
  })

  describe('validateEmail', () => {
    const validateEmail = (email: string) => {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return re.test(email)
    }

    it('should validate correct email format', () => {
      expect(validateEmail('test@example.com')).toBe(true)
      expect(validateEmail('user.name@domain.co')).toBe(true)
    })

    it('should reject invalid email format', () => {
      expect(validateEmail('invalid-email')).toBe(false)
      expect(validateEmail('test@')).toBe(false)
      expect(validateEmail('@example.com')).toBe(false)
    })
  })

  describe('truncateText', () => {
    const truncateText = (text: string, maxLength: number) => {
      if (text.length <= maxLength) return text
      return text.slice(0, maxLength) + '...'
    }

    it('should not truncate short text', () => {
      expect(truncateText('Short', 10)).toBe('Short')
    })

    it('should truncate long text', () => {
      expect(truncateText('This is a very long text', 10)).toBe('This is a ...')
    })

    it('should handle empty string', () => {
      expect(truncateText('', 10)).toBe('')
    })
  })

  describe('debounce', () => {
    vi.useFakeTimers()

    it('should debounce function calls', () => {
      const mockFn = vi.fn()
      const debouncedFn = debounce(mockFn, 100)

      debouncedFn()
      debouncedFn()
      debouncedFn()

      expect(mockFn).not.toHaveBeenCalled()

      vi.advanceTimersByTime(100)

      expect(mockFn).toHaveBeenCalledTimes(1)
    })
  })
})

function debounce(fn: Function, delay: number) {
  let timeoutId: NodeJS.Timeout
  return (...args: any[]) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}
