import type { Message } from './message'

export interface Conversation {
  id: string
  title: string
  createdAt: string
  updatedAt: string
  messages: Message[]
}

export interface ConversationSummary {
  id: string
  title: string
  createdAt: string
  updatedAt: string
}
