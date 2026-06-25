import { useEffect, useState } from 'react'

export default function Typewriter({ text, speed = 70, className = '' }: {
  text: string; speed?: number; className?: string
}) {
  const [n, setN] = useState(0)
  useEffect(() => {
    const reduce = typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    if (reduce) { setN(text.length); return }
    const id = setInterval(() => {
      setN((prev) => {
        if (prev >= text.length) { clearInterval(id); return prev }
        return prev + 1
      })
    }, speed)
    return () => clearInterval(id)
  }, [text, speed])
  return (
    <span className={`font-mono ${className}`}>
      {text.slice(0, n)}<span className="blink" aria-hidden="true" />
    </span>
  )
}
