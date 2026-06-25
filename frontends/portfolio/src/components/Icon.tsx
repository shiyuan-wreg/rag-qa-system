import { FileSearch, Terminal, Workflow, GraduationCap, FileText, RefreshCw, ExternalLink, type LucideIcon } from 'lucide-react'

export type IconName = 'file-search' | 'terminal' | 'workflow' | 'graduation-cap' | 'file-text' | 'refresh-cw' | 'external-link'

// 换图标库时:只改这张表(把右侧组件替换为新库组件即可)
const MAP: Record<IconName, LucideIcon> = {
  'file-search': FileSearch,
  'terminal': Terminal,
  'workflow': Workflow,
  'graduation-cap': GraduationCap,
  'file-text': FileText,
  'refresh-cw': RefreshCw,
  'external-link': ExternalLink,
}

export default function Icon({ name, className = 'w-5 h-5', strokeWidth = 1.6 }: {
  name: IconName
  className?: string
  strokeWidth?: number
}) {
  const C = MAP[name]
  return <C className={className} strokeWidth={strokeWidth} aria-hidden="true" />
}
