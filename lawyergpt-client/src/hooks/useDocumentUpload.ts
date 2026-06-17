import { useCallback, useState } from 'react'
import { documentApi } from '../services/documentApi'
import type { LegalDocument, DocumentStatus } from '../types/document'

interface UploadState {
  document: LegalDocument | null
  uploading: boolean
  error: string | null
}

export function useDocumentUpload() {
  const [state, setState] = useState<UploadState>({
    document: null,
    uploading: false,
    error: null,
  })

  const upload = useCallback(async (file: File) => {
    setState({ document: null, uploading: true, error: null })
    try {
      const doc = await documentApi.upload(file)
      setState({ document: doc, uploading: false, error: null })
      return doc
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Upload failed'
      setState({ document: null, uploading: false, error: message })
      return null
    }
  }, [])

  const pollStatus = useCallback(
    async (
      id: string,
      onUpdate: (status: DocumentStatus) => void,
    ): Promise<DocumentStatus> => {
      return new Promise((resolve) => {
        const interval = setInterval(async () => {
          try {
            const doc = await documentApi.get(id)
            onUpdate(doc.status)
            if (doc.status === 'completed' || doc.status === 'failed') {
              clearInterval(interval)
              resolve(doc.status)
            }
          } catch {
            clearInterval(interval)
            resolve('failed')
          }
        }, 3000)
      })
    },
    [],
  )

  const reset = useCallback(() => {
    setState({ document: null, uploading: false, error: null })
  }, [])

  return { ...state, upload, pollStatus, reset }
}
