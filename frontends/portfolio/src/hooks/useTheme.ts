import { useEffect, useState } from 'react'

export type Theme = 'mono-light' | 'mono' | 'light' | 'deepblue' | 'cyber'

const STORAGE_KEY = 'ai-demos-theme'
const DEFAULT_THEME: Theme = 'mono-light'
const ALL_THEMES: Theme[] = ['mono-light', 'mono', 'light', 'deepblue', 'cyber']

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
    window.localStorage.setItem(STORAGE_KEY, theme)
  }, [theme])

  const setTheme = (t: Theme) => setThemeState(t)

  return { theme, setTheme }
}
