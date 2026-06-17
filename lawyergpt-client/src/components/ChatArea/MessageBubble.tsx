import { CitationList } from '../CitationPanel/CitationList'
import type { Message } from '../../types/message'

interface Props {
  message: Message
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === 'user'

  return (
    <div
      data-testid={`message-${message.role}`}
      className={`flex gap-4 py-6 px-4 md:px-8 ${isUser ? 'flex-row-reverse' : ''}`}
    >
      <div
        className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-white text-sm font-bold ${
          isUser ? 'bg-blue-600' : 'bg-emerald-600'
        }`}
      >
        {isUser ? 'U' : 'AI'}
      </div>

      <div className={`flex-1 min-w-0 ${isUser ? 'flex flex-col items-end' : ''}`}>
        {isUser ? (
          <div className="bg-blue-600 text-white rounded-2xl rounded-tr-sm px-4 py-2 max-w-xl">
            <p className="leading-relaxed whitespace-pre-wrap">{message.content}</p>
          </div>
        ) : (
          <>
            <p className="text-gray-100 leading-relaxed whitespace-pre-wrap">
              {message.content}
            </p>
            {message.citations.length > 0 && (
              <CitationList citations={message.citations} />
            )}
          </>
        )}
      </div>
    </div>
  )
}
