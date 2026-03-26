import { expect, test } from '@playwright/test'

import { expectChatShell, getChatProviderConfig, provisionRemoteChatAccess } from './helpers/chat'

test.describe('Chat Interaction', () => {
  test('should open a published remote-backed chat application', async ({ page }) => {
    test.skip(
      !(await getChatProviderConfig()),
      'Requires SiliconCloud credentials in .env.local-dev to provision a remote-backed chat application.',
    )

    const { chatUrl } = await provisionRemoteChatAccess(page)

    await page.goto(chatUrl)
    await expect(page).toHaveURL(/\/[^/?]+\?mode=pc$/)
    await expectChatShell(page)
  })
})
