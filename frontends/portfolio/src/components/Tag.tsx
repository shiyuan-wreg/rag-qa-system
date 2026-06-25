export default function Tag({ children }: { children: React.ReactNode }) {
  return (
    <span className="font-mono text-[11px] tracking-wide text-tertiary border border-border-subtle rounded px-2 py-0.5">
      {children}
    </span>
  )
}
