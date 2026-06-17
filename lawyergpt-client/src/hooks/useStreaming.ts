import { useCallback, useRef } from 'react'
import { useConversationStore } from '../store/conversationStore'
import { useUiStore } from '../store/uiStore'
import type { Citation } from '../types/citation'
import type { Message } from '../types/message'

interface SSETokenEvent { type: 'token'; content: string }
interface SSECitationsEvent { type: 'citations'; content: Citation[] }
interface SSEDoneEvent { type: 'done'; message: Message }
type SSEEvent = SSETokenEvent | SSECitationsEvent | SSEDoneEvent

export function useStreaming() {
  const abortRef = useRef<AbortController | null>(null)
  const {
    setIsStreaming,
    appendStreamingContent,
    setStreamingCitations,
    clearStreaming,
    finalizeStreamedMessage,
  } = useConversationStore()
  const { setErrorMessage } = useUiStore()

  const sendMessage = useCallback(
    async (conversationId: string, content: string, modelId: string) => {
      abortRef.current = new AbortController()
      setIsStreaming(true)
      clearStreaming()

      let response: Response
      try {
        response = await fetch(
          `http://localhost:8000/api/conversations/${conversationId}/messages`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ role: 'user', content, model: modelId }),
            signal: abortRef.current.signal,
          },
        )
      } catch (err) {
        setIsStreaming(false)
        if (err instanceof DOMException && err.name === 'AbortError') return
        setErrorMessage(
          'Backend server is not running on port 8000. Start the server to get AI responses.',
        )
        throw err
      }

      if (!response.ok || !response.body) {
        setIsStreaming(false)
        const msg =
          response.status === 404
            ? 'Conversation not found — please click "New Chat" and try again.'
            : `Server error: HTTP ${response.status}`
        setErrorMessage(msg)
        throw new Error(`HTTP ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() ?? ''

          for (const line of lines) {
            if (!line.startsWith('data: ')) continue
            const raw = line.slice(6).trim()
            if (!raw) continue

            let event: SSEEvent
            try {
              event = JSON.parse(raw) as SSEEvent
            } catch {
              continue
            }

            if (event.type === 'token') {
              appendStreamingContent(event.content)
            } else if (event.type === 'citations') {
              setStreamingCitations(event.content)
            } else if (event.type === 'done') {
              finalizeStreamedMessage(event.message)
            }
          }
        }
      } finally {
        setIsStreaming(false)
      }
    },
    [
      setIsStreaming,
      clearStreaming,
      appendStreamingContent,
      setStreamingCitations,
      finalizeStreamedMessage,
      setErrorMessage,
    ],
  )

  const abort = useCallback(() => {
    abortRef.current?.abort()
    clearStreaming()
  }, [clearStreaming])

  return { sendMessage, abort }
}
