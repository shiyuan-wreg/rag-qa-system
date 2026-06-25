import { FileSearch, Terminal, Workflow, GraduationCap, FileText, type LucideIcon } from 'lucide-react'

export type IconName = 'file-search' | 'terminal' | 'workflow' | 'graduation-cap' | 'file-text'

// 换图标库时:只改这张表(把右侧组件替换为新库组件即可)
const MAP: Record<IconName, LucideIcon> = {
  'file-search': FileSearch,
  'terminal': Terminal,
  'workflow': Workflow,
  'graduation-cap': GraduationCap,
  'file-text': FileText,
}

export default function Icon({ name, className = 'w-5 h-5', strokeWidth = 1.6 }: {
  name: IconName
  className?: string
  strokeWidth?: number
}) {
  const C = MAP[name]
  return <C className={className} strokeWidth={strokeWidth} aria-hidden="true" />
}
