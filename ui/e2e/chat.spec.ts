import { testWithCleanup as test, expect } from './fixtures'

import {
  expectChatShell,
  getChatProviderConfig,
  provisionRemoteChatAccessWithCleanup,
} from './helpers/chat'

test.describe('Chat Interaction', () => {
  test('should open a published remote-backed chat application', async ({ page, resourceTracker }) => {
    test.skip(
      !(await getChatProviderConfig()),
      'Requires SiliconCloud credentials in .env.local-dev to provision a remote-backed chat application.',
    )

    const { chatUrl } = await provisionRemoteChatAccessWithCleanup(page, resourceTracker)

    await page.goto(chatUrl)
    await expect(page).toHaveURL(/\/[^/?]+\?mode=pc$/)
    await expectChatShell(page)
  })
})
