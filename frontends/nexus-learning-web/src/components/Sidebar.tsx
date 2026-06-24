import { BookOpen, CheckCircle2, Circle, ChevronDown, Trophy, RotateCcw } from 'lucide-react'
import type { Module, Lesson } from '../types/course'

interface SidebarProps {
  modules: Module[]
  currentLessonId: string
  completedLessons: string[]
  onSelectLesson: (lessonId: string) => void
  total: number
  completed: number
  wrongCount: number
  onReset: () => void
}

export default function Sidebar({
  modules,
  currentLessonId,
  completedLessons,
  onSelectLesson,
  total,
  completed,
  wrongCount,
  onReset,
}: SidebarProps) {
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0

  return (
    <aside className="w-72 bg-white border-r border-slate-200 h-screen overflow-y-auto sticky top-0">
      <div className="p-5 border-b border-slate-100">
        <div className="flex items-center gap-2 text-primary-600 mb-1">
          <BookOpen size={22} />
          <span className="font-bold text-lg">Nexus 学习</span>
        </div>
        <p className="text-xs text-slate-500">从 LLM 到 Multi-Agent 工程落地</p>
      </div>

      <div className="px-5 py-4 border-b border-slate-100">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-1.5 text-sm font-medium text-slate-700">
            <Trophy size={15} className="text-warning" />
            学习进度
          </div>
          <span className="text-sm font-bold text-primary-600">{percentage}%</span>
        </div>
        <div className="w-full bg-slate-200 rounded-full h-2 mb-2">
          <div
            className="bg-primary-600 h-2 rounded-full transition-all duration-500"
            style={{ width: `${percentage}%` }}
          />
        </div>
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>
            {completed}/{total} 节完成
            {wrongCount > 0 && <span className="text-danger"> · 错题 {wrongCount}</span>}
          </span>
          <button
            onClick={onReset}
            className="flex items-center gap-1 text-slate-400 hover:text-danger transition-colors"
          >
            <RotateCcw size={12} />
            重置
          </button>
        </div>
      </div>

      <nav className="p-3">
        {modules.map((module) => (
          <ModuleSection
            key={module.id}
            module={module}
            currentLessonId={currentLessonId}
            completedLessons={completedLessons}
            onSelectLesson={onSelectLesson}
          />
        ))}
      </nav>
    </aside>
  )
}

function ModuleSection({
  module,
  currentLessonId,
  completedLessons,
  onSelectLesson,
}: {
  module: Module
  currentLessonId: string
  completedLessons: string[]
  onSelectLesson: (lessonId: string) => void
}) {
  const hasCurrent = module.lessons.some(l => l.id === currentLessonId)
  const completedCount = module.lessons.filter(l => completedLessons.includes(l.id)).length
  const isCompleted = completedCount === module.lessons.length

  return (
    <div className="mb-3">
      <div className={`flex items-center justify-between px-3 py-2 rounded-lg text-sm font-semibold ${
        hasCurrent ? 'bg-primary-50 text-primary-700' : 'text-slate-700'
      }`}>
        <div className="flex items-center gap-2">
          {isCompleted ? <CheckCircle2 size={16} className="text-success" /> : <ChevronDown size={16} />}
          <span>{module.title}</span>
        </div>
        <span className="text-xs text-slate-400">{completedCount}/{module.lessons.length}</span>
      </div>

      <div className="mt-1 space-y-0.5">
        {module.lessons.map((lesson) => (
          <LessonItem
            key={lesson.id}
            lesson={lesson}
            isActive={lesson.id === currentLessonId}
            isCompleted={completedLessons.includes(lesson.id)}
            onClick={() => onSelectLesson(lesson.id)}
          />
        ))}
      </div>
    </div>
  )
}

function LessonItem({
  lesson,
  isActive,
  isCompleted,
  onClick,
}: {
  lesson: Lesson
  isActive: boolean
  isCompleted: boolean
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-2 px-3 py-2 text-left text-sm rounded-lg transition-colors ${
        isActive
          ? 'bg-primary-100 text-primary-800 font-medium'
          : 'text-slate-600 hover:bg-slate-50'
      }`}
    >
      {isCompleted ? (
        <CheckCircle2 size={16} className="text-success shrink-0" />
      ) : (
        <Circle size={16} className={`shrink-0 ${isActive ? 'text-primary-500' : 'text-slate-300'}`} />
      )}
      <span className="truncate">{lesson.order}. {lesson.title}</span>
    </button>
  )
}
