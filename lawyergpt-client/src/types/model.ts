export interface AIModel {
  id: string
  label: string
  description: string
  badge?: string
}

export const AVAILABLE_MODELS: AIModel[] = [
  {
    id: 'gpt-5.5',
    label: 'GPT-5.5',
    description: 'Most capable — best for complex legal analysis',
    badge: 'Latest',
  },
  {
    id: 'gpt-4o',
    label: 'GPT-4o',
    description: 'Fast and accurate — great for most queries',
  },
  {
    id: 'gpt-4o-mini',
    label: 'GPT-4o Mini',
    description: 'Fastest responses — ideal for quick lookups',
    badge: 'Fast',
  },
  {
    id: 'o3',
    label: 'o3',
    description: 'Deep reasoning — best for multi-step legal logic',
    badge: 'Reasoning',
  },
]

export const DEFAULT_MODEL_ID = 'gpt-4o'
