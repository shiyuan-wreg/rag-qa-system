import { type ButtonHTMLAttributes } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary'
}

export default function Button({ children, variant = 'primary', className = '', ...props }: ButtonProps) {
  const base = 'btn-lift inline-flex items-center justify-center px-5 py-2.5 rounded-full text-sm font-medium transition-all'
  const styles =
    variant === 'primary'
      ? 'bg-accent text-accent-text hover:opacity-90 shadow-sm hover:shadow-md'
      : 'bg-surface text-primary border border-border hover:bg-surface-hover hover:border-border'
  return (
    <button className={`${base} ${styles} ${className}`} {...props}>
      {children}
    </button>
  )
}
