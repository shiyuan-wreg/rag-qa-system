import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import '@fontsource/inter/400.css'
import '@fontsource/inter/500.css'
import '@fontsource/inter/600.css'
import '@fontsource/inter/700.css'
import '@fontsource/inter/800.css'
import '@fontsource/jetbrains-mono/400.css'
import '@fontsource/jetbrains-mono/500.css'
import './styles.css'

const stored = typeof window !== 'undefined'
  ? (window.localStorage.getItem('ai-demos-theme') as 'light' | 'deepblue' | 'cyber' | null)
  : null
if (stored && ['light', 'deepblue', 'cyber'].includes(stored)) {
  document.documentElement.setAttribute('data-theme', stored)
} else {
  document.documentElement.setAttribute('data-theme', 'light')
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
