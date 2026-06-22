import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import type { Lesson } from '../types/course'
import Quiz from './Quiz'
import CodeLab from './CodeLab'
import { CheckCircle2, Target, BookOpen, AlertTriangle, ExternalLink } from 'lucide-react'

interface LessonContentProps {
  lesson: Lesson
  onComplete: () => void
  isCompleted: boolean
}

export default function LessonContent({ lesson, onComplete, isCompleted }: LessonContentProps) {
  return (
    <article className="max-w-4xl mx-auto pb-20">
      {/* Header */}
      <header className="mb-8">
        <div className="text-sm text-primary-600 font-medium mb-2">{lesson.moduleTitle}</div>
        <h1 className="text-3xl font-bold text-slate-900 mb-3">{lesson.title}</h1>
        <p className="text-lg text-slate-600">{lesson.description}</p>
      </header>

      {/* Objectives */}
      <SectionCard icon={<Target size={20} />} title="本节目标" color="primary">
        <ul className="space-y-2">
          {lesson.objectives.map((obj, idx) => (
            <li key={idx} className="flex items-start gap-2 text-slate-700">
              <span className="text-primary-500 font-bold">{idx + 1}.</span>
              {obj}
            </li>
          ))}
        </ul>
      </SectionCard>

      {/* Prerequisites */}
      <SectionCard icon={<BookOpen size={20} />} title="前置检查" color="slate">
        <ul className="space-y-1.5">
          {lesson.prerequisites.map((pre, idx) => (
            <li key={idx} className="flex items-center gap-2 text-slate-600">
              <input type="checkbox" className="rounded text-primary-600" readOnly />
              {pre}
            </li>
          ))}
        </ul>
      </SectionCard>

      {/* Key Concepts */}
      <SectionCard icon={<BookOpen size={20} />} title="关键概念" color="slate">
        <div className="flex flex-wrap gap-2">
          {lesson.keyConcepts.map((concept, idx) => (
            <span
              key={idx}
              className="px-3 py-1 bg-slate-100 text-slate-700 rounded-full text-sm font-medium"
            >
              {concept}
            </span>
          ))}
        </div>
      </SectionCard>

      {/* Main Content */}
      <div className="bg-white rounded-xl border border-slate-200 p-8 shadow-sm mb-8">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeHighlight]}
          components={{
            code({ node, inline, className, children, ...props }: any) {
              const match = /language-(\w+)/.exec(className || '')
              return !inline && match ? (
                <SyntaxHighlighter
                  style={oneDark}
                  language={match[1]}
                  PreTag="div"
                  {...props}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              ) : (
                <code className={className} {...props}>{children}</code>
              )
            },
            table({ children }) {
              return (
                <div className="overflow-x-auto my-4">
                  <table className="min-w-full border-collapse border border-slate-300">{children}</table>
                </div>
              )
            },
            th({ children }) {
              return <th className="border border-slate-300 bg-slate-100 px-4 py-2 text-left font-semibold">{children}</th>
            },
            td({ children }) {
              return <td className="border border-slate-300 px-4 py-2">{children}</td>
            }
          }}
          className="prose-custom"
        >
          {lesson.content}
        </ReactMarkdown>
      </div>

      {/* Code Labs */}
      {lesson.codeLabs.length > 0 && (
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-slate-900 mb-4">代码实验室</h2>
          <div className="space-y-4">
            {lesson.codeLabs.map((lab) => (
              <CodeLab key={lab.id} lab={lab} />
            ))}
          </div>
        </div>
      )}

      {/* Quiz */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-900 mb-4">本节测验</h2>
        <Quiz questions={lesson.quizzes} />
      </div>

      {/* Common Mistakes */}
      <SectionCard icon={<AlertTriangle size={20} />} title="常见错误" color="warning">
        <ul className="space-y-2">
          {lesson.commonMistakes.map((mistake, idx) => (
            <li key={idx} className="flex items-start gap-2 text-slate-700">
              <span className="text-warning">•</span>
              {mistake}
            </li>
          ))}
        </ul>
      </SectionCard>

      {/* Further Reading */}
      <SectionCard icon={<ExternalLink size={20} />} title="进阶阅读" color="slate">
        <ul className="space-y-1.5">
          {lesson.furtherReading.map((item, idx) => (
            <li key={idx} className="text-slate-600">
              {item.url ? (
                <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">{item.title}</a>
              ) : (
                item.title
              )}
            </li>
          ))}
        </ul>
      </SectionCard>

      {/* Checklist */}
      <SectionCard icon={<CheckCircle2 size={20} />} title="本节检查清单" color="success">
        <ul className="space-y-1.5">
          {lesson.checklist.map((item, idx) => (
            <li key={idx} className="flex items-center gap-2 text-slate-700">
              <input type="checkbox" className="rounded text-success" />
              {item}
            </li>
          ))}
        </ul>
      </SectionCard>

      {/* Complete Button */}
      <div className="flex justify-end mt-8">
        <button
          onClick={onComplete}
          disabled={isCompleted}
          className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
            isCompleted
              ? 'bg-success text-white cursor-default'
              : 'bg-primary-600 text-white hover:bg-primary-700'
          }`}
        >
          {isCompleted ? '已完成本节' : '标记为完成'}
        </button>
      </div>
    </article>
  )
}

function SectionCard({
  icon,
  title,
  color,
  children,
}: {
  icon: React.ReactNode
  title: string
  color: 'primary' | 'success' | 'warning' | 'slate'
  children: React.ReactNode
}) {
  const colorClasses = {
    primary: 'bg-primary-50 border-primary-200 text-primary-800',
    success: 'bg-emerald-50 border-emerald-200 text-emerald-800',
    warning: 'bg-amber-50 border-amber-200 text-amber-800',
    slate: 'bg-slate-50 border-slate-200 text-slate-800',
  }

  return (
    <div className={`rounded-xl border p-5 mb-6 ${colorClasses[color]}`}>
      <div className="flex items-center gap-2 font-semibold mb-3">
        {icon}
        <span>{title}</span>
      </div>
      {children}
    </div>
  )
}
