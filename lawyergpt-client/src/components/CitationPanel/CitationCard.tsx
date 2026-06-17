import { useState } from 'react'
import type { Citation } from '../../types/citation'

interface Props {
  citation: Citation
}

export function CitationCard({ citation }: Props) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div
      data-testid="citation-card"
      className="border border-gray-600 rounded-lg overflow-hidden bg-gray-800 text-sm"
    >
      <button
        data-testid="citation-toggle-button"
        className="w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-gray-700 transition-colors"
        onClick={() => setExpanded((v) => !v)}
        aria-expanded={expanded}
      >
        <span className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-600 text-white text-xs flex items-center justify-center font-bold">
          {citation.number}
        </span>
        <span className="flex-1 text-gray-300 truncate">{citation.sourceFile}</span>
        <span className="text-gray-500 text-xs">p.{citation.pageNumber}</span>
        <svg
          className={`w-4 h-4 text-gray-400 transition-transform ${expanded ? 'rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {expanded && (
        <div className="px-3 py-2 border-t border-gray-600 text-gray-400 leading-relaxed">
          {citation.excerpt}
        </div>
      )}
    </div>
  )
}
