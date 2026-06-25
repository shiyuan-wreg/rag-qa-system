export type TermLine = { type: 'cmd' | 'out'; text: string }

export default function FakeTerminal({ lines, title = 'shiyuan-wreg.cloud — zsh' }: {
  lines: TermLine[]; title?: string
}) {
  return (
    <div className="term font-mono text-[13px] max-w-xl mx-auto text-left">
      <div className="term__bar">
        <span className="term__dot" /><span className="term__dot" /><span className="term__dot" />
        <span className="ml-2 text-[11px] text-zinc-500 tracking-wide">{title}</span>
      </div>
      <div className="term__body">
        {lines.map((l, i) => (
          <div key={i} className={l.type === 'cmd' ? 'text-zinc-100' : 'text-zinc-400'}>
            {l.type === 'cmd' ? <span className="text-zinc-500">$ </span> : '  '}{l.text}
          </div>
        ))}
      </div>
    </div>
  )
}
