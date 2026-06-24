const PALETTE: Record<string, { bg: string; text: string }> = {
  blue: { bg: '#eff6ff', text: '#1d4ed8' },
  green: { bg: '#f0fdf4', text: '#15803d' },
  purple: { bg: '#faf5ff', text: '#7e22ce' },
  cyan: { bg: '#ecfeff', text: '#0e7490' },
  orange: { bg: '#fff7ed', text: '#c2410c' },
  red: { bg: '#fef2f2', text: '#b91c1c' },
  slate: { bg: '#f1f5f9', text: '#475569' },
}

export default function Tag({ children, color = 'blue' }: { children: React.ReactNode; color?: string }) {
  const p = PALETTE[color] ?? PALETTE.blue
  return (
    <span
      className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
      style={{ backgroundColor: p.bg, color: p.text }}
    >
      {children}
    </span>
  )
}
