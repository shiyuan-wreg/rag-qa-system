import { useState, useMemo } from 'react'
import { modules, getAllLessons, getNextLessonId, getPrevLessonId } from './data/course'
import { useProgress } from './hooks/useProgress'
import Sidebar from './components/Sidebar'
import LessonContent from './components/LessonContent'
import ProgressBar from './components/ProgressBar'
import { ChevronLeft, ChevronRight, RotateCcw } from 'lucide-react'

function App() {
  const allLessons = useMemo(() => getAllLessons(), [])
  const [currentLessonId, setCurrentLessonId] = useState(allLessons[0]?.id || '')
  const {
    progress,
    loaded,
    completeLesson,
    resetProgress,
  } = useProgress()

  const currentLesson = useMemo(
    () => allLessons.find(l => l.id === currentLessonId) || allLessons[0],
    [allLessons, currentLessonId]
  )

  const handleComplete = () => {
    if (currentLesson) {
      completeLesson(currentLesson.id)
    }
  }

  const handleNext = () => {
    const nextId = getNextLessonId(currentLessonId)
    if (nextId) setCurrentLessonId(nextId)
  }

  const handlePrev = () => {
    const prevId = getPrevLessonId(currentLessonId)
    if (prevId) setCurrentLessonId(prevId)
  }

  if (!loaded) {
    return (
      <div className="min-h-screen flex items-center justify-center"
      >
        <div className="text-slate-500">加载中...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex"
    >
      <Sidebar
        modules={modules}
        currentLessonId={currentLessonId}
        completedLessons={progress.completedLessons}
        onSelectLesson={setCurrentLessonId}
      />

      <div className="flex-1 flex flex-col min-h-screen"
      >
        <ProgressBar
          total={allLessons.length}
          completed={progress.completedLessons.length}
          wrongCount={progress.wrongQuestions.length}
        />

        <main className="flex-1 px-8 py-6"
        >
          <div className="max-w-5xl mx-auto"
          >
            {/* Navigation */}
            <div className="flex items-center justify-between mb-6"
            >
              <button
                onClick={handlePrev}
                disabled={!getPrevLessonId(currentLessonId)}
                className="flex items-center gap-1 px-4 py-2 text-sm text-slate-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeft size={18} />
                上一节
              </button>

              <button
                onClick={resetProgress}
                className="flex items-center gap-1.5 px-3 py-2 text-sm text-slate-500 hover:text-danger hover:bg-red-50 rounded-lg transition-colors"
              >
                <RotateCcw size={16} />
                重置进度
              </button>

              <button
                onClick={handleNext}
                disabled={!getNextLessonId(currentLessonId)}
                className="flex items-center gap-1 px-4 py-2 text-sm text-slate-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                下一节
                <ChevronRight size={18} />
              </button>
            </div>

            {currentLesson ? (
              <LessonContent
                lesson={currentLesson}
                onComplete={handleComplete}
                isCompleted={progress.completedLessons.includes(currentLesson.id)}
              />
            ) : (
              <div className="text-center py-20 text-slate-500"
              >暂无课程内容</div>
            )}

            {/* Bottom Navigation */}
            <div className="flex items-center justify-between mt-8 pt-6 border-t border-slate-200"
            >
              <button
                onClick={handlePrev}
                disabled={!getPrevLessonId(currentLessonId)}
                className="flex items-center gap-2 px-5 py-2.5 border border-slate-300 rounded-lg text-slate-700 hover:border-primary-500 hover:text-primary-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeft size={18} />
                上一节
              </button>

              <button
                onClick={handleNext}
                disabled={!getNextLessonId(currentLessonId)}
                className="flex items-center gap-2 px-5 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                下一节
                <ChevronRight size={18} />
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

export default App
