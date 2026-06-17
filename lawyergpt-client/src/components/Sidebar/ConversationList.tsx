import { useConversation } from '../../hooks/useConversation'
import { useConversationStore } from '../../store/conversationStore'
import type { ConversationSummary } from '../../types/conversation'

function groupByDate(conversations: ConversationSummary[]) {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today)
  yesterday.setDate(today.getDate() - 1)
  const lastWeek = new Date(today)
  lastWeek.setDate(today.getDate() - 7)

  const groups: Record<string, ConversationSummary[]> = {
    Today: [],
    Yesterday: [],
    'Last 7 Days': [],
    Older: [],
  }

  for (const c of conversations) {
    const d = new Date(c.createdAt)
    if (d >= today) groups.Today.push(c)
    else if (d >= yesterday) groups.Yesterday.push(c)
    else if (d >= lastWeek) groups['Last 7 Days'].push(c)
    else groups.Older.push(c)
  }

  return groups
}

export function ConversationList() {
  const { conversations, selectConversation, deleteConversation } = useConversation()
  const { activeConversationId } = useConversationStore()
  const groups = groupByDate(conversations)

  return (
    <div data-testid="conversation-list" className="flex-1 overflow-y-auto py-2">
      {Object.entries(groups).map(([label, items]) => {
        if (items.length === 0) return null
        return (
          <div key={label} className="mb-3">
            <p className="px-3 py-1 text-xs font-semibold text-gray-500 uppercase tracking-wide">
              {label}
            </p>
            {items.map((c) => (
              <div
                key={c.id}
                className={`group flex items-center px-3 py-2 rounded-lg mx-1 cursor-pointer transition-colors ${
                  c.id === activeConversationId
                    ? 'bg-gray-700 text-white'
                    : 'text-gray-400 hover:bg-gray-700 hover:text-white'
                }`}
                onClick={() => void selectConversation(c.id)}
                data-testid="conversation-item"
              >
                <span className="flex-1 truncate text-sm">{c.title}</span>
                <button
                  className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-gray-600 transition-all"
                  onClick={(e) => {
                    e.stopPropagation()
                    void deleteConversation(c.id)
                  }}
                  title="Delete conversation"
                >
                  <svg className="w-3.5 h-3.5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        )
      })}

      {conversations.length === 0 && (
        <p className="px-3 py-4 text-xs text-gray-600 text-center">No conversations yet</p>
      )}
    </div>
  )
}
