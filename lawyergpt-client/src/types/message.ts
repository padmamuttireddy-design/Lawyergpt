import type { Citation } from './citation'

export type MessageRole = 'user' | 'assistant'

export interface Message {
  id: string
  conversationId: string
  role: MessageRole
  content: string
  citations: Citation[]
  createdAt: string
}

export interface StreamingMessage {
  content: string
  citations: Citation[]
  isStreaming: boolean
}
