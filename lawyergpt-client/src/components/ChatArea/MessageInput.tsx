import { useState, useRef, type KeyboardEvent } from 'react'
import { useConversationStore } from '../../store/conversationStore'
import { useUiStore } from '../../store/uiStore'
import { useStreaming } from '../../hooks/useStreaming'
import { useConversation } from '../../hooks/useConversation'
import type { Message } from '../../types/message'

export function MessageInput() {
  const [text, setText] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const { activeConversationId, isStreaming, addMessage } = useConversationStore()
  const { selectedModelId } = useUiStore()
  const { sendMessage, abort } = useStreaming()
  const { createConversation } = useConversation()

  const handleSend = async () => {
    const trimmed = text.trim()
    if (!trimmed || isStreaming) return

    setText('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }

    let conversationId = activeConversationId
    if (!conversationId) {
      const convo = await createConversation()
      if (!convo) {
        setText(trimmed)
        return
      }
      conversationId = convo.id
    }

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      conversationId,
      role: 'user',
      content: trimmed,
      citations: [],
      createdAt: new Date().toISOString(),
    }
    addMessage(userMessage)

    try {
      await sendMessage(conversationId, trimmed, selectedModelId)
    } catch (err) {
      // Error already displayed by useStreaming — restore text so user can retry
      setText(trimmed)
      // If conversation not found (stale local ID), clear the active conversation
      // so the next send will auto-create a real one
      if (err instanceof Error && err.message.includes('404')) {
        const { setActiveConversation } = useConversationStore.getState()
        setActiveConversation(null)
      }
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      void handleSend()
    }
  }

  const handleInput = () => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`
  }

  return (
    <div className="border-t border-gray-700 bg-gray-800 px-4 py-4">
      <div className="max-w-3xl mx-auto flex items-end gap-3">
        <div className="flex-1 bg-gray-700 rounded-xl border border-gray-600 focus-within:border-blue-500 transition-colors">
          <textarea
            ref={textareaRef}
            data-testid="message-input"
            className="w-full bg-transparent text-gray-100 placeholder-gray-500 resize-none px-4 py-3 focus:outline-none text-sm leading-relaxed"
            placeholder="Ask a legal question..."
            rows={1}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            onInput={handleInput}
            disabled={isStreaming}
          />
        </div>

        {isStreaming ? (
          <button
            data-testid="stop-button"
            onClick={abort}
            className="w-10 h-10 rounded-lg bg-red-600 hover:bg-red-500 flex items-center justify-center transition-colors flex-shrink-0"
            title="Stop generating"
          >
            <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
              <rect x="6" y="6" width="12" height="12" />
            </svg>
          </button>
        ) : (
          <button
            data-testid="send-button"
            onClick={() => void handleSend()}
            disabled={!text.trim()}
            className="w-10 h-10 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:bg-gray-600 disabled:cursor-not-allowed flex items-center justify-center transition-colors flex-shrink-0"
            title="Send message"
          >
            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19V5m0 0l-7 7m7-7l7 7" />
            </svg>
          </button>
        )}
      </div>
      <p className="text-center text-xs text-gray-600 mt-2">
        Shift+Enter for new line · Enter to send
      </p>
    </div>
  )
}
