import { describe, expect, it } from 'vitest'

import { FORCE_PASSWORD_CHANGE_ROUTE_NAME, getPasswordChangeRedirect } from '@/router/index'

describe('force password change guard', () => {
  it('redirects flagged users into the forced password change route', () => {
    expect(getPasswordChangeRedirect('home', true)).toEqual({
      name: FORCE_PASSWORD_CHANGE_ROUTE_NAME,
    })
  })

  it('allows flagged users to stay on the forced password change route', () => {
    expect(getPasswordChangeRedirect(FORCE_PASSWORD_CHANGE_ROUTE_NAME, true)).toBeNull()
  })

  it('redirects unflagged users away from the forced password change route', () => {
    expect(getPasswordChangeRedirect(FORCE_PASSWORD_CHANGE_ROUTE_NAME, false)).toEqual({
      name: 'home',
    })
  })

  it('leaves normal navigation untouched for unflagged users', () => {
    expect(getPasswordChangeRedirect('application', false)).toBeNull()
  })
})
