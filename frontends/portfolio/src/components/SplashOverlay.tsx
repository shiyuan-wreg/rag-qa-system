import { useEffect, useState } from 'react'

export const BLACK_HOLD_MS = 500
export const FADE_DURATION_MS = 1800
export const TOTAL_SPLASH_MS = BLACK_HOLD_MS + FADE_DURATION_MS

type SplashPhase = 'black' | 'fading' | 'done'

export default function SplashOverlay() {
  const [phase, setPhase] = useState<SplashPhase>('black')

  useEffect(() => {
    const fadeTimer = window.setTimeout(() => setPhase('fading'), BLACK_HOLD_MS)
    const doneTimer = window.setTimeout(() => setPhase('done'), TOTAL_SPLASH_MS)

    return () => {
      window.clearTimeout(fadeTimer)
      window.clearTimeout(doneTimer)
    }
  }, [])

  if (phase === 'done') return null

  return (
    <div
      aria-hidden="true"
      className={`fixed inset-0 z-[100] bg-black pointer-events-none transition-opacity ease-out ${
        phase === 'fading' ? 'opacity-0' : 'opacity-100'
      }`}
      style={{ transitionDuration: `${FADE_DURATION_MS}ms` }}
    />
  )
}
