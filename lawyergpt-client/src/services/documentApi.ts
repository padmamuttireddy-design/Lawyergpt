import api from './api'
import type { LegalDocument } from '../types/document'

export const documentApi = {
  async upload(file: File): Promise<LegalDocument> {
    const form = new FormData()
    form.append('file', file)
    const { data } = await api.post<LegalDocument>('/api/documents/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },

  async list(): Promise<LegalDocument[]> {
    const { data } = await api.get<LegalDocument[]>('/api/documents')
    return data
  },

  async get(id: string): Promise<LegalDocument> {
    const { data } = await api.get<LegalDocument>(`/api/documents/${id}`)
    return data
  },
}
