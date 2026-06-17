import { useConversation } from '../../hooks/useConversation'

export function NewChatButton() {
  const { createConversation } = useConversation()

  return (
    <button
      data-testid="new-chat-button"
      onClick={() => void createConversation()}
      className="flex items-center gap-3 w-full px-3 py-2 rounded-lg border border-gray-600 text-gray-300 hover:bg-gray-700 transition-colors text-sm"
    >
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
      </svg>
      New chat
    </button>
  )
}
