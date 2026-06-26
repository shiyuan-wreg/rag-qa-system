import { useEffect, useRef } from 'react'
import type { ReactNode } from 'react'
import { useMotionPreference } from '../hooks/useMotionPreference'

// 全局 3D 视差:ParallaxToggle 开启时,鼠标在页面内移动 → 整页内容轻微倾斜。
// 不限主题、不限页面(取代原先只在 MachineSkin 内生效的版本)。
export default function ParallaxViewport({ children }: { children: ReactNode }) {
  const { effectiveParallax } = useMotionPreference()
  const viewportRef = useRef<HTMLDivElement>(null)
  const contentRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!effectiveParallax) return
    const viewport = viewportRef.current
    const content = contentRef.current
    if (!viewport || !content) return

    let frame = 0
    let latest: MouseEvent | null = null
    const onMove = (e: MouseEvent) => {
      latest = e
      if (frame) return
      frame = window.requestAnimationFrame(() => {
        frame = 0
        const ev = latest
        latest = null
        if (!ev) return
        const rect = viewport.getBoundingClientRect()
        const nx = (ev.clientX - rect.left) / rect.width - 0.5   // [-0.5, 0.5]
        const ny = (ev.clientY - rect.top) / rect.height - 0.5
        content.style.transform =
          `rotateX(${-ny * 6}deg) rotateY(${nx * 6}deg) translate3d(${nx * 6}px, ${ny * 6}px, 0)`
      })
    }
    const reset = () => {
      if (frame) {
        window.cancelAnimationFrame(frame)
        frame = 0
      }
      latest = null
      content.style.transform = ''
    }

    viewport.addEventListener('mousemove', onMove)
    viewport.addEventListener('mouseleave', reset)
    return () => {
      viewport.removeEventListener('mousemove', onMove)
      viewport.removeEventListener('mouseleave', reset)
      reset()
    }
  }, [effectiveParallax])

  return (
    <div ref={viewportRef} className="parallax-viewport">
      <div ref={contentRef} className="parallax-content">{children}</div>
    </div>
  )
}
