import { useEffect, useState } from 'react'

const STORAGE_KEY = 'ai-demos-parallax'
const SYNC_EVENT = 'ai-demos-parallax-change'

function readEnabled(): boolean {
  if (typeof window === 'undefined') return false
  return window.localStorage.getItem(STORAGE_KEY) === 'true'
}

function readReducedMotion(): boolean {
  if (typeof window === 'undefined') return false
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

export function useMotionPreference() {
  const [parallaxEnabled, setEnabled] = useState<boolean>(readEnabled)
  const [prefersReducedMotion, setReduced] = useState<boolean>(readReducedMotion)

  useEffect(() => {
    if (typeof window === 'undefined') return

    const sync = () => setEnabled(readEnabled())
    window.addEventListener(SYNC_EVENT, sync)
    window.addEventListener('storage', sync)

    const mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    const onMq = () => setReduced(mq.matches)
    mq.addEventListener('change', onMq)

    return () => {
      window.removeEventListener(SYNC_EVENT, sync)
      window.removeEventListener('storage', sync)
      mq.removeEventListener('change', onMq)
    }
  }, [])

  const setParallaxEnabled = (v: boolean) => {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(STORAGE_KEY, String(v))
      window.dispatchEvent(new Event(SYNC_EVENT))
    }
    setEnabled(v)
  }

  return {
    parallaxEnabled,
    setParallaxEnabled,
    prefersReducedMotion,
    effectiveParallax: parallaxEnabled && !prefersReducedMotion,
  }
}
