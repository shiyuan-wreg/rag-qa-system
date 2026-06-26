import { useEffect, useRef } from 'react'
import type { ReactNode } from 'react'
import { useMotionPreference } from '../hooks/useMotionPreference'

export default function MachineSkin({ children }: { children: ReactNode }) {
  const { effectiveParallax } = useMotionPreference()
  const viewportRef = useRef<HTMLDivElement>(null)
  const contentRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!effectiveParallax) return
    const viewport = viewportRef.current
    const content = contentRef.current
    if (!viewport || !content) return

    let frame = 0
    const onMove = (e: MouseEvent) => {
      if (frame) return
      frame = window.requestAnimationFrame(() => {
        frame = 0
        const rect = viewport.getBoundingClientRect()
        const nx = (e.clientX - rect.left) / rect.width - 0.5   // [-0.5, 0.5]
        const ny = (e.clientY - rect.top) / rect.height - 0.5
        const rotateY = nx * 12   // 上限 ±6°
        const rotateX = -ny * 12
        const tx = nx * 8
        const ty = ny * 8
        content.style.transform =
          `rotateX(${rotateX}deg) rotateY(${rotateY}deg) translate3d(${tx}px, ${ty}px, 0)`
      })
    }
    const reset = () => {
      if (frame) {
        window.cancelAnimationFrame(frame)
        frame = 0
      }
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
    <div className="machine-skin flex-1 min-h-0 flex flex-col">
      <div className="machine-skin__grid" aria-hidden="true" />
      <div className="machine-skin__noise" aria-hidden="true" />
      <div className="machine-skin__vignette" aria-hidden="true" />
      <div className="machine-skin__scanline" aria-hidden="true" />
      <div className="machine-skin__frame" aria-hidden="true">
        <span /><span /><span /><span />
      </div>
      <div ref={viewportRef} className="machine-skin__viewport">
        <div ref={contentRef} className="machine-skin__content">{children}</div>
      </div>
    </div>
  )
}
