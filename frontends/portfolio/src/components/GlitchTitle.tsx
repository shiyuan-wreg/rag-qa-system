export default function GlitchTitle({ text, className = '' }: { text: string; className?: string }) {
  return (
    <h1
      className={`scatter-title text-4xl md:text-6xl font-extrabold tracking-tight text-primary ${className}`}
    >
      {text}
    </h1>
  )
}
