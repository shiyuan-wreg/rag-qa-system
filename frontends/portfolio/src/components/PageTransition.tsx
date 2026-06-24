import { useEffect, useState, type ReactNode } from 'react'

export default function PageTransition({ children }: { children: ReactNode }) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <div
      className="transition-all duration-200 ease-out"
      style={{
        opacity: mounted ? 1 : 0,
        transform: mounted ? 'translateY(0)' : 'translateY(8px)',
      }}
    >
      {children}
    </div>
  )
}
