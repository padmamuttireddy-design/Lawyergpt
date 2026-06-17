export type DocumentStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface LegalDocument {
  id: string
  filename: string
  filePath: string
  status: DocumentStatus
  error: string | null
  createdAt: string
  updatedAt: string
}
