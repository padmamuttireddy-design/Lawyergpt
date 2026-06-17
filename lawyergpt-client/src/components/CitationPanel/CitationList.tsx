import { CitationCard } from './CitationCard'
import type { Citation } from '../../types/citation'

interface Props {
  citations: Citation[]
}

export function CitationList({ citations }: Props) {
  if (citations.length === 0) return null

  return (
    <div data-testid="citation-list" className="mt-3 flex flex-col gap-2">
      <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">Sources</p>
      {citations.map((c) => (
        <CitationCard key={c.id} citation={c} />
      ))}
    </div>
  )
}
