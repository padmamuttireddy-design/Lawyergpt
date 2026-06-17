import { useRef, useState, type DragEvent, type ChangeEvent } from 'react'

interface Props {
  onFile: (file: File) => void
  disabled?: boolean
}

export function DropZone({ onFile, disabled }: Props) {
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file && file.type === 'application/pdf') onFile(file)
  }

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) onFile(file)
  }

  return (
    <div
      data-testid="dropzone"
      className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
        dragging
          ? 'border-blue-500 bg-blue-500/10'
          : 'border-gray-600 hover:border-gray-500 hover:bg-gray-700/50'
      } ${disabled ? 'opacity-50 pointer-events-none' : ''}`}
      onDragOver={(e) => {
        e.preventDefault()
        setDragging(true)
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={handleChange}
        disabled={disabled}
      />
      <svg
        className="w-10 h-10 mx-auto mb-3 text-gray-500"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
        />
      </svg>
      <p className="text-gray-300 font-medium mb-1">Drop a PDF here</p>
      <p className="text-gray-500 text-sm">or click to browse files</p>
    </div>
  )
}
