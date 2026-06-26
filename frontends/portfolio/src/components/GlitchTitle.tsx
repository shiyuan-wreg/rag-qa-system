export default function GlitchTitle({ text, className = '' }: { text: string; className?: string }) {
  return (
    <h1
      data-text={text}
      className={`glitch is-on text-4xl md:text-6xl font-extrabold tracking-tight text-primary ${className}`}
    >
      {text}
    </h1>
  )
}
