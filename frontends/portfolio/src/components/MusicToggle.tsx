interface MusicToggleProps {
  isMuted: boolean
  onToggle: () => void
}

function MusicNoteIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
      aria-hidden="true"
    >
      <path d="M9.5 4.5v11.18a4.001 4.001 0 1 1-2-3.464V12l9-2v7.18a4.001 4.001 0 1 1-2-3.464V4l-5 1.5z" />
    </svg>
  )
}

function MusicNoteOffIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
      aria-hidden="true"
    >
      <path d="M1.5 1.5 22.5 22.5" stroke="currentColor" strokeWidth="2" />
      <path d="M9.5 4.5v11.18a4.001 4.001 0 1 1-2-3.464V12l9-2v7.18a4.001 4.001 0 1 1-2-3.464V4l-5 1.5z" />
    </svg>
  )
}

export default function MusicToggle({ isMuted, onToggle }: MusicToggleProps) {
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-label={isMuted ? '开启背景音乐' : '关闭背景音乐'}
      title={isMuted ? '背景音乐已关闭' : '背景音乐已开启'}
      className="p-2 rounded-md text-tertiary hover:text-primary hover:bg-surface-hover transition-colors active:scale-95"
    >
      {isMuted ? (
        <MusicNoteOffIcon className="w-5 h-5" />
      ) : (
        <MusicNoteIcon className="w-5 h-5" />
      )}
    </button>
  )
}
