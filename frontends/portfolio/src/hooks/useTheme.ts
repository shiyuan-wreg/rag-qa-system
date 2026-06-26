import { useEffect, useState } from 'react'

export type Theme = 'mono-light' | 'mono' | 'light' | 'deepblue' | 'cyber' | 'machine'

const STORAGE_KEY = 'ai-demos-theme'
const SYNC_EVENT = 'ai-demos-theme-change'
const DEFAULT_THEME: Theme = 'mono-light'
export const ALL_THEMES: Theme[] = ['mono-light', 'light', 'deepblue', 'cyber', 'machine']

function getInitialTheme(): Theme {
  if (typeof window === 'undefined') return DEFAULT_THEME
  const stored = window.localStorage.getItem(STORAGE_KEY) as Theme | null
  if (stored && ALL_THEMES.includes(stored)) return stored
  return DEFAULT_THEME
}

export function useTheme() {
  const [theme, setThemeState] = useState<Theme>(getInitialTheme)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  useEffect(() => {
    if (typeof window === 'undefined') return
    const sync = () => {
      const stored = window.localStorage.getItem(STORAGE_KEY) as Theme | null
      if (stored && ALL_THEMES.includes(stored)) setThemeState(stored)
    }
    window.addEventListener(SYNC_EVENT, sync)
    window.addEventListener('storage', sync)
    return () => {
      window.removeEventListener(SYNC_EVENT, sync)
      window.removeEventListener('storage', sync)
    }
  }, [])

  const setTheme = (t: Theme) => {
    setThemeState(t)
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(STORAGE_KEY, t)
      window.dispatchEvent(new Event(SYNC_EVENT))
    }
  }

  return { theme, setTheme }
}
