export default function Logo({ className = 'w-8 h-8' }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 512 512"
      fill="currentColor"
      aria-hidden="true"
      className={className}
    >
      <title>ai-demos</title>
      <polygon points="40,180 90,40 130,40 80,180" />
      <polygon points="80,240 130,100 170,100 120,240" />
      <polygon points="120,420 190,120 310,120 260,420 190,420 210,340 170,340 150,420" />
      <polygon points="225,260 245,180 285,180 265,260" fill-opacity="0.35" />
      <polygon points="330,420 380,120 460,120 410,420" />
      <polygon points="420,40 460,80 420,120 380,80" fill-opacity="0.55" />
    </svg>
  )
}
