import { useState, useRef, useEffect } from 'react'
import { AVAILABLE_MODELS } from '../../types/model'
import { useUiStore } from '../../store/uiStore'

const BADGE_COLORS: Record<string, string> = {
  Latest: 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30',
  Fast: 'bg-blue-500/20 text-blue-400 border border-blue-500/30',
  Reasoning: 'bg-violet-500/20 text-violet-400 border border-violet-500/30',
}

export function ModelSelector() {
  const { selectedModelId, setSelectedModelId } = useUiStore()
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  const selected = AVAILABLE_MODELS.find((m) => m.id === selectedModelId) ?? AVAILABLE_MODELS[0]

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  return (
    <div ref={ref} className="relative" data-testid="model-selector">
      <button
        data-testid="model-selector-button"
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-700/60 hover:bg-gray-700 border border-gray-600/50 hover:border-gray-500 transition-all text-sm text-gray-200 font-medium"
      >
        <svg className="w-3.5 h-3.5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        <span>{selected.label}</span>
        {selected.badge && (
          <span className={`text-[10px] px-1.5 py-0.5 rounded font-semibold ${BADGE_COLORS[selected.badge] ?? ''}`}>
            {selected.badge}
          </span>
        )}
        <svg
          className={`w-3.5 h-3.5 text-gray-400 transition-transform ${open ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div
          data-testid="model-dropdown"
          className="absolute top-full left-0 mt-2 w-72 bg-gray-800 border border-gray-600 rounded-xl shadow-2xl z-50 overflow-hidden"
        >
          <div className="px-3 py-2 border-b border-gray-700">
            <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Select Model</p>
          </div>
          {AVAILABLE_MODELS.map((model) => {
            const isActive = model.id === selectedModelId
            return (
              <button
                key={model.id}
                data-testid={`model-option-${model.id}`}
                onClick={() => {
                  setSelectedModelId(model.id)
                  setOpen(false)
                }}
                className={`w-full flex items-start gap-3 px-4 py-3 text-left transition-colors hover:bg-gray-700 ${
                  isActive ? 'bg-gray-700/70' : ''
                }`}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className={`text-sm font-semibold ${isActive ? 'text-amber-400' : 'text-gray-200'}`}>
                      {model.label}
                    </span>
                    {model.badge && (
                      <span className={`text-[10px] px-1.5 py-0.5 rounded font-semibold ${BADGE_COLORS[model.badge] ?? ''}`}>
                        {model.badge}
                      </span>
                    )}
                    {isActive && (
                      <svg className="w-3.5 h-3.5 text-amber-400 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5">{model.description}</p>
                </div>
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}
