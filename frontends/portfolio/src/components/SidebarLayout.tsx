import { type ReactNode } from 'react'

export default function SidebarLayout({ sidebar, children }: { sidebar: ReactNode; children: ReactNode }) {
  return (
    <div className="h-full flex flex-col lg:flex-row gap-6">
      <aside className="lg:w-64 shrink-0">
        <div className="hud-frame lg:sticky lg:top-20 max-h-[calc(100vh-6rem)] overflow-y-auto bg-surface border border-border rounded-xl p-3 shadow-sm">
          {sidebar}
        </div>
      </aside>
      <main className="flex-1 min-w-0 h-full min-h-0">{children}</main>
    </div>
  )
}
