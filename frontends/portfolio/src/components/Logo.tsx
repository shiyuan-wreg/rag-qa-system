export default function Logo({ className = 'h-8 w-auto' }: { className?: string }) {
  return (
    <img
      src="/logo.svg"
      alt="Kairos"
      className={`logo-img ${className}`}
    />
  )
}
