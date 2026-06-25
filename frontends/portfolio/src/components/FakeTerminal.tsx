export type TermLine = { type: 'cmd' | 'out'; text: string }

export default function FakeTerminal({ lines, title = 'shiyuan-wreg.cloud — zsh' }: {
  lines: TermLine[]; title?: string
}) {
  return (
    <div className="term font-mono text-[13px] text-secondary max-w-xl mx-auto text-left">
      <div className="term__bar">
        <span className="term__dot" /><span className="term__dot" /><span className="term__dot" />
        <span className="ml-2 text-[11px] text-muted tracking-wide">{title}</span>
      </div>
      <div className="term__body">
        {lines.map((l, i) => (
          <div key={i} className={l.type === 'cmd' ? 'text-primary' : 'text-tertiary'}>
            {l.type === 'cmd' ? <span className="text-muted">$ </span> : '  '}{l.text}
          </div>
        ))}
      </div>
    </div>
  )
}
