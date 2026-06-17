import { test, expect } from '@playwright/test'

const BASE_URL = 'http://localhost:3000'

test.describe('LawyerGPT Client', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/conversations', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'default-conv',
            title: 'New Chat',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            messages: [],
          }),
        })
      }
    })
    await page.goto(BASE_URL)
    await page.waitForLoadState('networkidle')
  })

  test('renders the main layout with sidebar and chat area', async ({ page }) => {
    await expect(page.getByTestId('sidebar')).toBeVisible()
    await expect(page.getByTestId('message-list')).toBeVisible()
    await expect(page.getByTestId('message-input')).toBeVisible()
    await expect(page.getByTestId('new-chat-button')).toBeVisible()
    await expect(page.getByTestId('upload-docs-button')).toBeVisible()
    await expect(page.getByTestId('model-selector')).toBeVisible()
  })

  test('model selector shows GPT-4o as default', async ({ page }) => {
    const selector = page.getByTestId('model-selector-button')
    await expect(selector).toBeVisible()
    await expect(selector).toContainText('GPT-4o')
  })

  test('model selector opens dropdown and allows switching models', async ({ page }) => {
    await page.getByTestId('model-selector-button').click()
    await expect(page.getByTestId('model-dropdown')).toBeVisible()

    await expect(page.getByTestId('model-option-gpt-5.5')).toBeVisible()
    await expect(page.getByTestId('model-option-gpt-4o')).toBeVisible()
    await expect(page.getByTestId('model-option-gpt-4o-mini')).toBeVisible()
    await expect(page.getByTestId('model-option-o3')).toBeVisible()

    await page.getByTestId('model-option-gpt-4o').click()
    await expect(page.getByTestId('model-dropdown')).not.toBeVisible()
    await expect(page.getByTestId('model-selector-button')).toContainText('GPT-4o')
  })

  test('model selector closes when clicking outside', async ({ page }) => {
    await page.getByTestId('model-selector-button').click()
    await expect(page.getByTestId('model-dropdown')).toBeVisible()

    await page.mouse.click(10, 300)
    await expect(page.getByTestId('model-dropdown')).not.toBeVisible()
  })

  test('selected model is included in message request body', async ({ page }) => {
    let capturedBody: Record<string, unknown> = {}

    await page.route('**/api/conversations/default-conv/messages', async (route) => {
      capturedBody = JSON.parse(route.request().postData() ?? '{}') as Record<string, unknown>
      const sseBody = 'data: {"type":"done","message":{"id":"m1","conversationId":"default-conv","role":"assistant","content":"ok","citations":[],"createdAt":"2024-01-01T00:00:00Z"}}\n\n'
      await route.fulfill({ status: 200, contentType: 'text/event-stream', body: sseBody })
    })

    await page.getByTestId('model-selector-button').click()
    await page.getByTestId('model-option-o3').click()

    await page.getByTestId('new-chat-button').click()
    await page.getByTestId('message-input').fill('What is the statute of limitations?')
    await page.getByTestId('send-button').click()

    await page.waitForTimeout(500)
    expect(capturedBody['model']).toBe('o3')
  })

  test('new chat button creates a new conversation', async ({ page }) => {
    await page.getByTestId('new-chat-button').click()
    await expect(page.getByTestId('message-list')).toBeVisible()
    await expect(page.getByTestId('message-input')).toBeVisible()
  })

  test('message input is present and accepts text', async ({ page }) => {
    await page.getByTestId('new-chat-button').click()
    const input = page.getByTestId('message-input')
    await input.fill('What are the grounds for contract termination?')
    await expect(input).toHaveValue('What are the grounds for contract termination?')
  })

  test('send button is enabled when input has text', async ({ page }) => {
    await page.getByTestId('new-chat-button').click()
    const sendBtn = page.getByTestId('send-button')
    await expect(sendBtn).toBeDisabled()

    await page.getByTestId('message-input').fill('test question')
    await expect(sendBtn).not.toBeDisabled()
  })

  test('upload modal opens and closes', async ({ page }) => {
    await page.getByTestId('upload-docs-button').click()
    await expect(page.getByTestId('upload-modal')).toBeVisible()
    await expect(page.getByTestId('dropzone')).toBeVisible()

    await page.getByTestId('close-modal-button').click()
    await expect(page.getByTestId('upload-modal')).not.toBeVisible()
  })

  test('upload modal closes when clicking overlay', async ({ page }) => {
    await page.getByTestId('upload-docs-button').click()
    await expect(page.getByTestId('upload-modal')).toBeVisible()

    await page.mouse.click(10, 10)
    await expect(page.getByTestId('upload-modal')).not.toBeVisible()
  })

  test('sending a message shows user bubble and triggers streaming (with mock server)', async ({
    page,
  }) => {
    let messagePosted = false

    await page.route('**/api/conversations/default-conv/messages', async (route) => {
      messagePosted = true
      const sseBody = [
        'data: {"type":"token","content":"Under"}\n\n',
        'data: {"type":"token","content":" contract"}\n\n',
        'data: {"type":"token","content":" law,"}\n\n',
        'data: {"type":"citations","content":[{"id":"c1","messageId":"m1","number":1,"sourceFile":"contract_law.pdf","pageNumber":5,"excerpt":"Contracts may be terminated...","chunkId":"chunk-1"}]}\n\n',
        'data: {"type":"done","message":{"id":"m1","conversationId":"default-conv","role":"assistant","content":"Under contract law,","citations":[{"id":"c1","messageId":"m1","number":1,"sourceFile":"contract_law.pdf","pageNumber":5,"excerpt":"Contracts may be terminated...","chunkId":"chunk-1"}],"createdAt":"2024-01-01T00:00:00Z"}}\n\n',
      ].join('')

      await route.fulfill({
        status: 200,
        contentType: 'text/event-stream',
        body: sseBody,
      })
    })

    await page.getByTestId('new-chat-button').click()
    const input = page.getByTestId('message-input')
    await input.fill('What are grounds for contract termination?')
    await page.getByTestId('send-button').click()

    await expect(page.getByTestId('message-user').first()).toBeVisible({ timeout: 5000 })
    expect(messagePosted).toBe(true)
  })

  test('citation card expands and collapses', async ({ page }) => {
    await page.route('**/api/conversations/conv-with-citations', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'conv-with-citations',
          title: 'Legal Q&A',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          messages: [
            {
              id: 'msg-1',
              conversationId: 'conv-with-citations',
              role: 'user',
              content: 'What are grounds for termination?',
              citations: [],
              createdAt: new Date().toISOString(),
            },
            {
              id: 'msg-2',
              conversationId: 'conv-with-citations',
              role: 'assistant',
              content: 'Contracts may be terminated under several conditions [1]',
              citations: [
                {
                  id: 'cit-1',
                  messageId: 'msg-2',
                  number: 1,
                  sourceFile: 'contract_law.pdf',
                  pageNumber: 12,
                  excerpt: 'A contract may be terminated by mutual agreement...',
                  chunkId: 'chunk-abc',
                },
              ],
              createdAt: new Date().toISOString(),
            },
          ],
        }),
      })
    })

    await page.route('**/api/conversations', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            {
              id: 'conv-with-citations',
              title: 'Legal Q&A',
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString(),
            },
          ]),
        })
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 'default-conv',
            title: 'New Chat',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            messages: [],
          }),
        })
      }
    })

    await page.goto(BASE_URL)
    await page.waitForLoadState('networkidle')

    await page.getByTestId('conversation-item').first().click()
    await expect(page.getByTestId('citation-list')).toBeVisible({ timeout: 3000 })

    const card = page.getByTestId('citation-card').first()
    const toggleBtn = card.getByTestId('citation-toggle-button')

    await toggleBtn.click()
    await expect(card.locator('text=A contract may be terminated')).toBeVisible()

    await toggleBtn.click()
    await expect(card.locator('text=A contract may be terminated')).not.toBeVisible()
  })

  test('page title is LawyerGPT', async ({ page }) => {
    await expect(page).toHaveTitle('LawyerGPT')
  })
})
