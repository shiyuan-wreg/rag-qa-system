import { useEffect, useState } from 'react'

export default function Typewriter({ text, speed = 70, className = '' }: {
  text: string; speed?: number; className?: string
}) {
  const [n, setN] = useState(0)
  const [done, setDone] = useState(false)
  useEffect(() => {
    setN(0)
    setDone(false)
    const reduce = typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    if (reduce) { setN(text.length); setDone(true); return }
    const id = setInterval(() => {
      setN((prev) => {
        if (prev >= text.length) {
          clearInterval(id)
          setDone(true)
          return prev
        }
        return prev + 1
      })
    }, speed)
    return () => clearInterval(id)
  }, [text, speed])
  return (
    <span className={`font-mono ${className}`} aria-label={text}>
      {text.slice(0, n)}
      <span
        className={`inline-block align-middle ml-0.5 border-r-2 border-current ${done ? 'animate-blink-slow' : 'animate-blink'}`}
        style={{ height: '0.9em' }}
        aria-hidden="true"
      />
    </span>
  )
}
