import { CitationList } from '../CitationPanel/CitationList'
import { useConversationStore } from '../../store/conversationStore'

export function StreamingMessage() {
  const { streamingContent, streamingCitations, isStreaming } = useConversationStore()

  if (!isStreaming && !streamingContent) return null

  return (
    <div data-testid="streaming-message" className="flex gap-4 py-6 px-4 md:px-8">
      <div className="w-8 h-8 rounded-full bg-emerald-600 flex-shrink-0 flex items-center justify-center text-white text-sm font-bold">
        AI
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-gray-100 leading-relaxed whitespace-pre-wrap">
          {streamingContent}
          {isStreaming && (
            <span className="inline-block w-2 h-4 bg-gray-400 ml-0.5 animate-pulse" />
          )}
        </p>
        {streamingCitations.length > 0 && (
          <CitationList citations={streamingCitations} />
        )}
      </div>
    </div>
  )
}
