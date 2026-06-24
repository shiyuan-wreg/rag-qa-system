import { useState, useRef, useEffect } from 'react'

interface DemoFrameProps {
  src: string
  title: string
  showToolbar?: boolean
}

function ExternalIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
      <polyline points="15 3 21 3 21 9" />
      <line x1="10" y1="14" x2="21" y2="3" />
    </svg>
  )
}

function RefreshIcon({ spinning }: { spinning?: boolean }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={spinning ? 'animate-spin' : ''} aria-hidden="true">
      <polyline points="23 4 23 10 17 10" />
      <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
    </svg>
  )
}

export default function DemoFrame({ src, title, showToolbar = true }: DemoFrameProps) {
  const [status, setStatus] = useState<'loading' | 'loaded' | 'error'>('loading')
  const timerRef = useRef<number | null>(null)
  const loadedRef = useRef(false)

  const handleLoad = () => {
    if (timerRef.current) window.clearTimeout(timerRef.current)
    loadedRef.current = true
    setStatus('loaded')
  }

  const handleError = () => {
    if (timerRef.current) window.clearTimeout(timerRef.current)
    loadedRef.current = false
    setStatus('error')
  }

  const startLoad = () => {
    loadedRef.current = false
    setStatus('loading')
    if (timerRef.current) window.clearTimeout(timerRef.current)
    timerRef.current = window.setTimeout(() => {
      if (!loadedRef.current) setStatus('error')
    }, 8000)
  }

  const reload = () => {
    startLoad()
    setStatus('loading')
  }

  useEffect(() => {
    startLoad()
    return () => {
      if (timerRef.current) window.clearTimeout(timerRef.current)
    }
  }, [src])

  return (
    <div className="flex flex-col h-full bg-surface border border-border rounded-xl shadow-md overflow-hidden">
      {showToolbar && (
        <div className="flex items-center justify-between gap-3 px-4 py-3 border-b border-border-subtle bg-surface-soft">
          <div className="min-w-0">
            <h2 className="text-sm font-semibold text-primary truncate">{title}</h2>
            <p className="text-xs text-muted truncate hidden sm:block">{src}</p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={reload}
              disabled={status === 'loading'}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-secondary hover:text-primary hover:bg-surface-hover disabled:opacity-50 transition-colors"
              aria-label="刷新"
            >
              <RefreshIcon spinning={status === 'loading'} />
              <span className="hidden sm:inline">刷新</span>
            </button>
            <a
              href={src}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-accent text-accent-text hover:opacity-90 transition-opacity"
            >
              <ExternalIcon />
              <span className="hidden sm:inline">新窗口</span>
            </a>
          </div>
        </div>
      )}

      <div className="relative flex-1 min-h-0">
        {status === 'loading' && (
          <div className="absolute inset-0 p-5 space-y-4 z-10 bg-surface-soft">
            <div className="flex gap-3">
              <div className="h-8 w-32 bg-soft rounded-md shimmer" />
              <div className="h-8 w-24 bg-soft rounded-md shimmer" />
            </div>
            <div className="h-40 bg-soft rounded-lg shimmer" />
            <div className="space-y-2">
              <div className="h-4 bg-soft rounded w-3/4 shimmer" />
              <div className="h-4 bg-soft rounded w-1/2 shimmer" />
            </div>
          </div>
        )}

        {status === 'error' && (
          <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center z-10 bg-surface-soft">
            <p className="text-primary font-medium">Demo 加载失败或超时</p>
            <p className="text-secondary text-sm mt-1">请检查网络或刷新重试</p>
            <div className="mt-4 flex gap-3">
              <button
                onClick={reload}
                className="px-4 py-2 rounded-full bg-accent text-accent-text text-sm font-medium hover:opacity-90"
              >
                重试
              </button>
              <a
                href="/"
                className="px-4 py-2 rounded-full border border-border text-primary text-sm font-medium hover:bg-surface-hover"
              >
                返回首页
              </a>
            </div>
          </div>
        )}

        <iframe
          key={status === 'error' ? 'error' : 'frame'}
          title={title}
          src={src}
          onLoad={handleLoad}
          onError={handleError}
          className="w-full h-full border-0 transition-opacity duration-300"
          style={{ opacity: status === 'loaded' ? 1 : 0 }}
        />
      </div>

      <style>{`
        .shimmer {
          background: linear-gradient(90deg, var(--surface-hover) 25%, var(--surface-default) 50%, var(--surface-hover) 75%);
          background-size: 200% 100%;
          animation: shimmer 1.5s infinite;
        }
        @keyframes shimmer {
          0% { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
      `}</style>
    </div>
  )
}
