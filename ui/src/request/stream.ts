import type { RequestContext } from '@/request/core'

export function createPostStream(getRequestContext: () => RequestContext) {
  return (url: string, data?: unknown) => {
    const { token, language } = getRequestContext()
    const headers: HeadersInit = { 'Content-Type': 'application/json' }

    if (token) {
      headers['AUTHORIZATION'] = `Bearer ${token}`
    }
    if (language) {
      headers['Accept-Language'] = `${language}`
    }

    return fetch(url, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
      headers,
    })
  }
}
