import api from './api'
import type { Conversation, ConversationSummary } from '../types/conversation'

export const conversationApi = {
  async list(): Promise<ConversationSummary[]> {
    const { data } = await api.get<ConversationSummary[]>('/api/conversations')
    return data
  },

  async get(id: string): Promise<Conversation> {
    const { data } = await api.get<Conversation>(`/api/conversations/${id}`)
    return data
  },

  async create(): Promise<Conversation> {
    const { data } = await api.post<Conversation>('/api/conversations')
    return data
  },

  async updateTitle(id: string, title: string): Promise<ConversationSummary> {
    const { data } = await api.patch<ConversationSummary>(`/api/conversations/${id}`, { title })
    return data
  },

  async remove(id: string): Promise<void> {
    await api.delete(`/api/conversations/${id}`)
  },
}
