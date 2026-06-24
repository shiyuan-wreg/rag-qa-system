import { useEffect } from 'react'

export function useDocumentTitle(title: string, hiddenTitle = '快回来继续探索 AI 作品!') {
  useEffect(() => {
    const original = document.title
    document.title = title

    const onVisibilityChange = () => {
      document.title = document.hidden ? hiddenTitle : title
    }

    document.addEventListener('visibilitychange', onVisibilityChange)
    return () => {
      document.removeEventListener('visibilitychange', onVisibilityChange)
      document.title = original
    }
  }, [title, hiddenTitle])
}
