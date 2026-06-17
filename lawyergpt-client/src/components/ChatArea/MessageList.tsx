import { useEffect, useRef } from 'react'
import { MessageBubble } from './MessageBubble'
import { StreamingMessage } from './StreamingMessage'
import { useConversationStore } from '../../store/conversationStore'

export function MessageList() {
  const { activeConversation, isStreaming } = useConversationStore()
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [activeConversation?.messages, isStreaming])

  const messages = activeConversation?.messages ?? []

  return (
    <div data-testid="message-list" className="flex-1 overflow-y-auto divide-y divide-gray-700/50">
      {!activeConversation && (
        <div className="flex flex-col items-center justify-center h-full text-gray-500 px-6">
          <div className="w-16 h-16 rounded-2xl bg-gray-700/60 border border-gray-600/40 flex items-center justify-center mb-5">
            <svg className="w-8 h-8 text-amber-400/70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <p className="text-lg font-semibold text-gray-300 mb-1">How can I help you today?</p>
          <p className="text-sm text-gray-500 text-center max-w-xs">
            Click <span className="text-gray-400 font-medium">New chat</span> in the sidebar or type a question below to get started.
          </p>
          <div className="mt-6 flex flex-col gap-2 w-full max-w-sm">
            {[
              'What are the grounds for contract termination?',
              'Explain the statute of limitations for civil claims.',
              'What constitutes intellectual property infringement?',
            ].map((hint) => (
              <div
                key={hint}
                className="px-4 py-2.5 rounded-lg border border-gray-700/60 bg-gray-800/50 text-gray-500 text-xs cursor-default hover:border-amber-500/30 hover:text-gray-400 transition-colors"
              >
                {hint}
              </div>
            ))}
          </div>
        </div>
      )}
      {activeConversation && messages.length === 0 && !isStreaming && (
        <div className="flex items-center justify-center h-full text-gray-500">
          <p className="text-sm">Ask your legal question below</p>
        </div>
      )}
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      <StreamingMessage />
      <div ref={bottomRef} />
    </div>
  )
}
