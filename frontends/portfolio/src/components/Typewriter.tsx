import { useEffect, useState } from 'react'

export default function Typewriter({
  text,
  speed = 70,
  delay = 0,
  className = '',
}: {
  text: string
  speed?: number
  delay?: number
  className?: string
}) {
  const [n, setN] = useState(0)
  const [done, setDone] = useState(false)
  const [started, setStarted] = useState(delay <= 0)

  useEffect(() => {
    if (delay <= 0) {
      setStarted(true)
      return
    }
    const startTimer = setTimeout(() => setStarted(true), delay)
    return () => clearTimeout(startTimer)
  }, [delay])

  useEffect(() => {
    if (!started) return

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
  }, [text, speed, started])

  return (
    <span className={`font-mono ${className}`} aria-label={text}>
      {started ? text.slice(0, n) : ''}
      {started && (
        <span
          className={`inline-block align-middle ml-0.5 border-r-2 border-current ${done ? 'animate-blink-slow' : 'animate-blink'}`}
          style={{ height: '0.9em' }}
          aria-hidden="true"
        />
      )}
    </span>
  )
}
