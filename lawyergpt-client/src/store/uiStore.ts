import { create } from 'zustand'
import { DEFAULT_MODEL_ID } from '../types/model'

interface UiState {
  uploadModalOpen: boolean
  sidebarOpen: boolean
  selectedModelId: string
  errorMessage: string | null
  openUploadModal: () => void
  closeUploadModal: () => void
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
  setSelectedModelId: (modelId: string) => void
  setErrorMessage: (message: string | null) => void
}

export const useUiStore = create<UiState>((set) => ({
  uploadModalOpen: false,
  sidebarOpen: true,
  selectedModelId: DEFAULT_MODEL_ID,
  errorMessage: null,

  openUploadModal: () => set({ uploadModalOpen: true }),
  closeUploadModal: () => set({ uploadModalOpen: false }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setSelectedModelId: (modelId) => set({ selectedModelId: modelId }),
  setErrorMessage: (message) => set({ errorMessage: message }),
}))
