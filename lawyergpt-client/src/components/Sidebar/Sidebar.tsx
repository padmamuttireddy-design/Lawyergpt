import { NewChatButton } from './NewChatButton'
import { ConversationList } from './ConversationList'
import { useUiStore } from '../../store/uiStore'

function ScalesLogo() {
  return (
    <svg
      viewBox="0 0 40 40"
      className="w-8 h-8 flex-shrink-0"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Horizontal beam */}
      <rect x="4" y="13" width="32" height="2.2" rx="1.1" fill="#f59e0b" />
      {/* Center post */}
      <rect x="18.9" y="6" width="2.2" height="28" rx="1.1" fill="#f59e0b" />
      {/* Top ornament */}
      <circle cx="20" cy="6" r="2.5" fill="#fbbf24" />
      {/* Base */}
      <rect x="13" y="33" width="14" height="2.2" rx="1.1" fill="#f59e0b" />
      {/* Left pan chain */}
      <line x1="9" y1="15" x2="7" y2="22" stroke="#fbbf24" strokeWidth="1.4" strokeLinecap="round" />
      <line x1="9" y1="15" x2="11" y2="22" stroke="#fbbf24" strokeWidth="1.4" strokeLinecap="round" />
      {/* Left pan */}
      <path d="M5 22 Q6 25.5 9 25.5 Q12 25.5 13 22 Z" fill="#fbbf24" opacity="0.9" />
      {/* Right pan chain */}
      <line x1="31" y1="15" x2="29" y2="22" stroke="#fbbf24" strokeWidth="1.4" strokeLinecap="round" />
      <line x1="31" y1="15" x2="33" y2="22" stroke="#fbbf24" strokeWidth="1.4" strokeLinecap="round" />
      {/* Right pan */}
      <path d="M27 22 Q28 25.5 31 25.5 Q34 25.5 35 22 Z" fill="#fbbf24" opacity="0.9" />
    </svg>
  )
}

export function Sidebar() {
  const { openUploadModal } = useUiStore()

  return (
    <aside
      data-testid="sidebar"
      className="w-64 flex-shrink-0 flex flex-col h-full border-r border-gray-700/60"
      style={{ background: 'linear-gradient(180deg, #0f1117 0%, #141720 100%)' }}
    >
      {/* Logo + branding */}
      <div className="px-4 pt-5 pb-4 border-b border-gray-700/60">
        <div className="flex items-center gap-3 mb-4">
          <div className="relative">
            <div className="absolute inset-0 rounded-xl bg-amber-500/20 blur-sm" />
            <div className="relative w-10 h-10 rounded-xl bg-gradient-to-br from-gray-800 to-gray-900 border border-amber-500/30 flex items-center justify-center shadow-lg">
              <ScalesLogo />
            </div>
          </div>
          <div className="leading-tight">
            <p className="text-base font-bold tracking-tight">
              <span className="text-white">Lawyer</span>
              <span className="text-amber-400">GPT</span>
            </p>
            <p className="text-[10px] text-gray-500 font-medium tracking-widest uppercase">
              Legal AI Assistant
            </p>
          </div>
        </div>
        <NewChatButton />
      </div>

      <ConversationList />

      <div className="p-3 border-t border-gray-700/60">
        <button
          data-testid="upload-docs-button"
          onClick={openUploadModal}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-gray-400 hover:bg-gray-800 hover:text-amber-400 transition-colors text-sm group"
        >
          <svg
            className="w-4 h-4 group-hover:text-amber-400 transition-colors"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          Upload Documents
        </button>
      </div>
    </aside>
  )
}
