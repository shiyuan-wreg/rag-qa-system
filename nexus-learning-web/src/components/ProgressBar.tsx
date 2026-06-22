import { Trophy } from 'lucide-react'

interface ProgressBarProps {
  total: number
  completed: number
  wrongCount: number
}

export default function ProgressBar({ total, completed, wrongCount }: ProgressBarProps) {
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0

  return (
    <div className="bg-white border-b border-slate-200 px-6 py-4 sticky top-0 z-10"
    >
      <div className="flex items-center justify-between mb-2"
      >
        <div className="flex items-center gap-3"
        >
          <Trophy size={20} className="text-warning" />
          <span className="font-semibold text-slate-900"
          >学习进度</span>
          <span className="text-sm text-slate-500"
          >{completed}/{total} 节完成</span>
        </div>
        <div className="flex items-center gap-4 text-sm"
        >
          {wrongCount > 0 && (
            <span className="text-danger font-medium"
            >错题本：{wrongCount} 题</span>
          )}
          <span className="font-bold text-primary-600"
          >{percentage}%</span>
        </div>
      </div>
      <div className="w-full bg-slate-200 rounded-full h-2.5"
      >
        <div
          className="bg-primary-600 h-2.5 rounded-full transition-all duration-500"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}
