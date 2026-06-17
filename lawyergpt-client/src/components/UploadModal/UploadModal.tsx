import { useState } from 'react'
import { DropZone } from './DropZone'
import { useUiStore } from '../../store/uiStore'
import { useDocumentUpload } from '../../hooks/useDocumentUpload'
import type { DocumentStatus } from '../../types/document'

export function UploadModal() {
  const { uploadModalOpen, closeUploadModal } = useUiStore()
  const { uploading, error, upload, pollStatus, reset } = useDocumentUpload()
  const [status, setStatus] = useState<DocumentStatus | null>(null)
  const [filename, setFilename] = useState<string | null>(null)

  if (!uploadModalOpen) return null

  const handleFile = async (file: File) => {
    setFilename(file.name)
    setStatus(null)
    const doc = await upload(file)
    if (!doc) return

    setStatus(doc.status)
    if (doc.status !== 'completed' && doc.status !== 'failed') {
      const final = await pollStatus(doc.id, setStatus)
      setStatus(final)
    }
  }

  const handleClose = () => {
    reset()
    setStatus(null)
    setFilename(null)
    closeUploadModal()
  }

  const statusLabel: Record<DocumentStatus, string> = {
    pending: 'Queued for processing...',
    processing: 'Processing document...',
    completed: 'Document ready for queries',
    failed: 'Processing failed',
  }

  const statusColor: Record<DocumentStatus, string> = {
    pending: 'text-yellow-400',
    processing: 'text-blue-400',
    completed: 'text-green-400',
    failed: 'text-red-400',
  }

  return (
    <div
      data-testid="upload-modal"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={(e) => e.target === e.currentTarget && handleClose()}
    >
      <div className="bg-gray-800 rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700">
          <h2 className="text-white font-semibold">Upload Document</h2>
          <button
            data-testid="close-modal-button"
            onClick={handleClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-6">
          <DropZone onFile={(f) => void handleFile(f)} disabled={uploading} />

          {uploading && (
            <div className="mt-4 flex items-center gap-3 text-blue-400 text-sm">
              <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Uploading {filename}...
            </div>
          )}

          {status && !uploading && (
            <div
              data-testid="upload-status"
              className={`mt-4 flex items-center gap-2 text-sm ${statusColor[status]}`}
            >
              {status === 'processing' && (
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              )}
              {statusLabel[status]}
            </div>
          )}

          {error && (
            <p className="mt-4 text-red-400 text-sm">{error}</p>
          )}

          {status === 'completed' && (
            <button
              onClick={handleClose}
              className="mt-4 w-full bg-green-600 hover:bg-green-500 text-white py-2 rounded-lg text-sm font-medium transition-colors"
            >
              Done — Start Asking Questions
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
