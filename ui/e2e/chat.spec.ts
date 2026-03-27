import { testWithCleanup as test, expect } from './fixtures'

import {
  expectChatShell,
  getChatProviderConfig,
  provisionRemoteChatAccessWithCleanup,
} from './helpers/chat'

test.describe('Chat Interaction', () => {
  test('should send a message to a published remote-backed chat application', async ({ page, resourceTracker }) => {
    test.skip(
      !(await getChatProviderConfig()),
      'Requires SiliconCloud credentials in .env.local-dev to provision a remote-backed chat application.',
    )

    const { chatUrl } = await provisionRemoteChatAccessWithCleanup(page, resourceTracker)
    const prompt = 'Please reply with one short sentence confirming the chat works.'

    await page.goto(chatUrl)
    await expect(page).toHaveURL(/\/[^/?]+\?mode=pc$/)
    await expectChatShell(page)

    const chatContent = page.locator('#chatListId')
    const initialText = await chatContent.innerText()

    await page.getByPlaceholder('Type your question').fill(prompt)
    await page.locator('.sent-button').click()

    await expect(chatContent).toContainText(prompt)
    await expect
      .poll(async () => {
        const text = await chatContent.innerText()
        return text.includes(prompt) && !text.includes('Generating Response') && text.length > initialText.length + 20
      }, { timeout: 60000 })
      .toBe(true)
  })
})
