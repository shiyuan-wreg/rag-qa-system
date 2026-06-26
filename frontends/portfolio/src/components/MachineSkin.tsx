import type { ReactNode } from 'react'

export default function MachineSkin({ children }: { children: ReactNode }) {
  return (
    <div className="machine-skin flex-1 min-h-0 flex flex-col">
      <div className="machine-skin__grid" aria-hidden="true" />
      <div className="machine-skin__noise" aria-hidden="true" />
      <div className="machine-skin__vignette" aria-hidden="true" />
      <div className="machine-skin__scanline" aria-hidden="true" />
      <div className="machine-skin__frame" aria-hidden="true">
        <span /><span /><span /><span />
      </div>
      <div className="machine-skin__viewport">
        <div className="machine-skin__content">{children}</div>
      </div>
    </div>
  )
}
