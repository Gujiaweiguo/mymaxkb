import { test as base } from '@playwright/test'

import { loginAsAdmin } from '../helpers/auth'
import { ResourceTracker, type TrackedResource } from '../helpers/data'
import { cleanupResources } from '../helpers/cleanup'

type E2EFixtures = {
  resourceTracker: ResourceTracker
}

export const test = base.extend<E2EFixtures>({
  resourceTracker: [
    async ({}, use) => {
      const tracker = new ResourceTracker()
      await use(tracker)
    },
    { scope: 'test' },
  ],
})

export const testWithCleanup = base.extend<E2EFixtures & { cleanup: void }>({
  resourceTracker: [
    async ({}, use) => {
      const tracker = new ResourceTracker()
      await use(tracker)
    },
    { scope: 'test' },
  ],
  cleanup: [
    async ({ page, resourceTracker }, use) => {
      await use(void 0)
      if (resourceTracker.count > 0) {
        await loginAsAdmin(page)
        await cleanupResources(page, resourceTracker.getAll())
      }
    },
    { scope: 'test', auto: true },
  ],
})

export { expect } from '@playwright/test'

export type { TrackedResource }
