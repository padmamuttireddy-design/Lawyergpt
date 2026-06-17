import { MessageList } from './MessageList'
import { MessageInput } from './MessageInput'
import { ModelSelector } from './ModelSelector'
import { useConversationStore } from '../../store/conversationStore'

export function ChatArea() {
  const { activeConversation } = useConversationStore()

  return (
    <div className="flex flex-col flex-1 h-full bg-gray-800 overflow-hidden">
      {/* Header bar */}
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-gray-700/60 bg-gray-800/95 backdrop-blur-sm flex-shrink-0">
        <div className="flex items-center gap-2 min-w-0">
          {activeConversation && (
            <h2 className="text-sm font-medium text-gray-300 truncate max-w-xs">
              {activeConversation.title}
            </h2>
          )}
        </div>
        <ModelSelector />
      </div>

      <MessageList />
      <MessageInput />
    </div>
  )
}
