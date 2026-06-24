export interface IconBoxProps {
  letter: string
  bg: string
  text: string
}

export default function IconBox({ letter, bg, text }: IconBoxProps) {
  return (
    <div
      className="w-10 h-10 rounded-md flex items-center justify-center text-sm font-bold shrink-0"
      style={{ backgroundColor: bg, color: text }}
    >
      {letter}
    </div>
  )
}
