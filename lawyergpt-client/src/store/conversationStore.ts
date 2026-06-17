import { create } from 'zustand'
import type { Conversation, ConversationSummary } from '../types/conversation'
import type { Message } from '../types/message'
import type { Citation } from '../types/citation'

interface ConversationState {
  conversations: ConversationSummary[]
  activeConversationId: string | null
  activeConversation: Conversation | null
  streamingContent: string
  streamingCitations: Citation[]
  isStreaming: boolean

  setConversations: (conversations: ConversationSummary[]) => void
  addConversation: (conversation: ConversationSummary) => void
  setActiveConversation: (conversation: Conversation | null) => void
  setActiveConversationId: (id: string | null) => void
  addMessage: (message: Message) => void
  updateConversationTitle: (id: string, title: string) => void
  removeConversation: (id: string) => void
  setStreamingContent: (content: string) => void
  appendStreamingContent: (token: string) => void
  setStreamingCitations: (citations: Citation[]) => void
  setIsStreaming: (streaming: boolean) => void
  clearStreaming: () => void
  finalizeStreamedMessage: (message: Message) => void
}

export const useConversationStore = create<ConversationState>((set) => ({
  conversations: [],
  activeConversationId: null,
  activeConversation: null,
  streamingContent: '',
  streamingCitations: [],
  isStreaming: false,

  setConversations: (conversations) => set({ conversations }),

  addConversation: (conversation) =>
    set((state) => ({
      conversations: [conversation, ...state.conversations],
    })),

  setActiveConversation: (conversation) =>
    set({
      activeConversation: conversation,
      activeConversationId: conversation?.id ?? null,
    }),

  setActiveConversationId: (id) => set({ activeConversationId: id }),

  addMessage: (message) =>
    set((state) => {
      if (!state.activeConversation) return state
      return {
        activeConversation: {
          ...state.activeConversation,
          messages: [...state.activeConversation.messages, message],
        },
      }
    }),

  updateConversationTitle: (id, title) =>
    set((state) => ({
      conversations: state.conversations.map((c) =>
        c.id === id ? { ...c, title } : c,
      ),
      activeConversation:
        state.activeConversation?.id === id
          ? { ...state.activeConversation, title }
          : state.activeConversation,
    })),

  removeConversation: (id) =>
    set((state) => ({
      conversations: state.conversations.filter((c) => c.id !== id),
      activeConversationId:
        state.activeConversationId === id ? null : state.activeConversationId,
      activeConversation:
        state.activeConversation?.id === id ? null : state.activeConversation,
    })),

  setStreamingContent: (content) => set({ streamingContent: content }),

  appendStreamingContent: (token) =>
    set((state) => ({ streamingContent: state.streamingContent + token })),

  setStreamingCitations: (citations) => set({ streamingCitations: citations }),

  setIsStreaming: (isStreaming) => set({ isStreaming }),

  clearStreaming: () =>
    set({ streamingContent: '', streamingCitations: [], isStreaming: false }),

  finalizeStreamedMessage: (message) =>
    set((state) => {
      if (!state.activeConversation) return state
      return {
        activeConversation: {
          ...state.activeConversation,
          messages: [...state.activeConversation.messages, message],
        },
        streamingContent: '',
        streamingCitations: [],
        isStreaming: false,
      }
    }),
}))
