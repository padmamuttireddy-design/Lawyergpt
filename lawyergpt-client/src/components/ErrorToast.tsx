import { useEffect } from 'react'
import { useUiStore } from '../store/uiStore'

export function ErrorToast() {
  const { errorMessage, setErrorMessage } = useUiStore()

  useEffect(() => {
    if (!errorMessage) return
    const timer = setTimeout(() => setErrorMessage(null), 5000)
    return () => clearTimeout(timer)
  }, [errorMessage, setErrorMessage])

  if (!errorMessage) return null

  return (
    <div
      data-testid="error-toast"
      className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 px-4 py-3 rounded-xl bg-red-950 border border-red-700 text-red-300 shadow-2xl text-sm max-w-sm w-full mx-4"
      role="alert"
    >
      <svg className="w-4 h-4 flex-shrink-0 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span className="flex-1">{errorMessage}</span>
      <button
        onClick={() => setErrorMessage(null)}
        className="text-red-500 hover:text-red-300 transition-colors flex-shrink-0"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  )
}
