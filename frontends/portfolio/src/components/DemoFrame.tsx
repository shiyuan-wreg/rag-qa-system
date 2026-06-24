import { useState, useRef } from 'react'

export default function DemoFrame({ src, title }: { src: string; title: string }) {
  const [status, setStatus] = useState<'loading' | 'loaded' | 'error'>('loading')
  const timerRef = useRef<number | null>(null)

  const handleLoad = () => {
    if (timerRef.current) window.clearTimeout(timerRef.current)
    setStatus('loaded')
  }

  const handleError = () => {
    if (timerRef.current) window.clearTimeout(timerRef.current)
    setStatus('error')
  }

  const startLoad = () => {
    setStatus('loading')
    if (timerRef.current) window.clearTimeout(timerRef.current)
    timerRef.current = window.setTimeout(() => {
      if (status !== 'loaded') setStatus('error')
    }, 8000)
  }

  const reload = () => {
    startLoad()
    setStatus('loading')
  }

  return (
    <div className="relative flex-1 min-h-[60vh] lg:min-h-[70vh] bg-surface border border-border rounded-xl shadow-sm overflow-hidden">
      {status === 'loading' && (
        <div className="absolute inset-0 p-5 space-y-4">
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
        <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center">
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
