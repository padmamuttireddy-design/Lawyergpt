import { useEffect } from 'react'
import { Sidebar } from './components/Sidebar/Sidebar'
import { ChatArea } from './components/ChatArea/ChatArea'
import { UploadModal } from './components/UploadModal/UploadModal'
import { ErrorToast } from './components/ErrorToast'
import { useConversation } from './hooks/useConversation'

export default function App() {
  const { loadConversations } = useConversation()

  useEffect(() => {
    void loadConversations()
  }, [loadConversations])

  return (
    <div className="flex h-screen bg-gray-800 text-gray-100 overflow-hidden">
      <Sidebar />
      <ChatArea />
      <UploadModal />
      <ErrorToast />
    </div>
  )
}
