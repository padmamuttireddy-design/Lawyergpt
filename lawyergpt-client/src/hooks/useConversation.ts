import { useCallback } from 'react'
import { conversationApi } from '../services/conversationApi'
import { useConversationStore } from '../store/conversationStore'
import { useUiStore } from '../store/uiStore'

function isNetworkError(err: unknown): boolean {
  return err instanceof TypeError && err.message.toLowerCase().includes('fetch')
}

function friendlyError(err: unknown): string {
  if (isNetworkError(err)) {
    return 'Backend server is not running on port 8000. Start the server to enable AI responses.'
  }
  if (err instanceof Error) return err.message
  return 'An unexpected error occurred.'
}

function makeLocalConversation() {
  const id = crypto.randomUUID()
  const now = new Date().toISOString()
  return { id, title: 'New Chat', createdAt: now, updatedAt: now, messages: [] }
}

export function useConversation() {
  const {
    conversations,
    activeConversationId,
    activeConversation,
    setConversations,
    addConversation,
    setActiveConversation,
    removeConversation,
    updateConversationTitle,
  } = useConversationStore()
  const { setErrorMessage } = useUiStore()

  const loadConversations = useCallback(async () => {
    try {
      const data = await conversationApi.list()
      setConversations(data)
    } catch {
      // Server not up yet — keep the store empty, no noise to the user
    }
  }, [setConversations])

  const selectConversation = useCallback(
    async (id: string) => {
      try {
        const convo = await conversationApi.get(id)
        setActiveConversation(convo)
      } catch (err) {
        setErrorMessage(friendlyError(err))
      }
    },
    [setActiveConversation, setErrorMessage],
  )

  const createConversation = useCallback(async () => {
    try {
      const convo = await conversationApi.create()
      addConversation({
        id: convo.id,
        title: convo.title,
        createdAt: convo.createdAt,
        updatedAt: convo.updatedAt,
      })
      setActiveConversation(convo)
      return convo
    } catch (err) {
      if (isNetworkError(err)) {
        // Server offline — create a local-only conversation so the UI stays usable
        const local = makeLocalConversation()
        addConversation({ id: local.id, title: local.title, createdAt: local.createdAt, updatedAt: local.updatedAt })
        setActiveConversation(local)
        return local
      }
      setErrorMessage(friendlyError(err))
      return null
    }
  }, [addConversation, setActiveConversation, setErrorMessage])

  const deleteConversation = useCallback(
    async (id: string) => {
      try {
        await conversationApi.remove(id)
      } catch {
        // Best-effort: remove locally even if server call fails
      }
      removeConversation(id)
    },
    [removeConversation],
  )

  const renameConversation = useCallback(
    async (id: string, title: string) => {
      try {
        await conversationApi.updateTitle(id, title)
      } catch {
        // Best-effort
      }
      updateConversationTitle(id, title)
    },
    [updateConversationTitle],
  )

  return {
    conversations,
    activeConversationId,
    activeConversation,
    loadConversations,
    selectConversation,
    createConversation,
    deleteConversation,
    renameConversation,
  }
}
