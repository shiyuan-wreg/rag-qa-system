import type { ReactNode } from 'react'
import { getLatestChangelog } from '../data/changelogs'

export default function MachineSkin({ children }: { children: ReactNode }) {
  const version = getLatestChangelog()?.version ?? '0.0.0'

  return (
    <div className="machine-skin flex-1 min-h-0 flex flex-col">
      <div className="machine-skin__grid" aria-hidden="true" />
      <div className="machine-skin__noise" aria-hidden="true" />
      <div className="machine-skin__vignette" aria-hidden="true" />
      <div className="machine-skin__scanline" aria-hidden="true" />
      <div className="machine-skin__frame" aria-hidden="true">
        <span /><span /><span /><span />
      </div>
      <div className="machine-skin__hud machine-skin__hud--tr" aria-hidden="true">
        <div className="rec">LIVE · MULTI-AGENT</div>
        <div>STATUS: ONLINE</div>
      </div>
      <div className="machine-skin__hud machine-skin__hud--bl" aria-hidden="true">
        <div>VERSION: v{version}</div>
        <div>MODEL: DEEPSEEK</div>
        <div>SYSTEM: UBUNTU · SEOUL</div>
      </div>
      <div className="machine-skin__viewport">
        <div className="machine-skin__content">{children}</div>
      </div>
    </div>
  )
}
