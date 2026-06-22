import { useState } from 'react'
import { CheckCircle2, XCircle, Lightbulb } from 'lucide-react'
import type { QuizQuestion } from '../types/course'

interface QuizProps {
  questions: QuizQuestion[]
}

export default function Quiz({ questions }: QuizProps) {
  const [answers, setAnswers] = useState<Record<string, string | string[]>>({})
  const [submitted, setSubmitted] = useState<Record<string, boolean>>({})

  const handleSelect = (questionId: string, optionId: string, type: string) => {
    if (submitted[questionId]) return

    if (type === 'multiple') {
      const current = (answers[questionId] as string[]) || []
      const updated = current.includes(optionId)
        ? current.filter(id => id !== optionId)
        : [...current, optionId]
      setAnswers(prev => ({ ...prev, [questionId]: updated }))
    } else {
      setAnswers(prev => ({ ...prev, [questionId]: optionId }))
    }
  }

  const handleCodeAnswer = (questionId: string, value: string) => {
    if (submitted[questionId]) return
    setAnswers(prev => ({ ...prev, [questionId]: value }))
  }

  const handleSubmit = (questionId: string) => {
    setSubmitted(prev => ({ ...prev, [questionId]: true }))
  }

  const isCorrect = (question: QuizQuestion): boolean => {
    const answer = answers[question.id]
    if (!answer) return false
    if (Array.isArray(question.correctAnswer)) {
      const selected = answer as string[]
      return selected.length === question.correctAnswer.length &&
        selected.every(id => question.correctAnswer.includes(id))
    }
    return answer === question.correctAnswer
  }

  return (
    <div className="space-y-6">
      {questions.map((question, index) => {
        const answered = submitted[question.id]
        const correct = answered ? isCorrect(question) : null

        return (
          <div
            key={question.id}
            className={`bg-white rounded-xl border p-6 transition-colors ${
              answered
                ? correct
                  ? 'border-success/50 bg-emerald-50/30'
                  : 'border-danger/50 bg-red-50/30'
                : 'border-slate-200'
            }`}
          >
            <div className="flex items-start gap-3 mb-4">
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center font-bold text-sm">
                {index + 1}
              </span>
              <div className="flex-1">
                <h3 className="font-semibold text-slate-900 mb-2">{question.question}</h3>
                {question.code && (
                  <pre className="bg-slate-900 text-slate-100 p-3 rounded-lg text-sm overflow-x-auto mb-3">
                    <code>{question.code}</code>
                  </pre>
                )}
              </div>
            </div>

            {question.type === 'code' ? (
              <div className="space-y-3">
                <input
                  type="text"
                  value={(answers[question.id] as string) || ''}
                  onChange={(e) => handleCodeAnswer(question.id, e.target.value)}
                  disabled={answered}
                  placeholder="输入你的答案..."
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-slate-100"
                />
              </div>
            ) : (
              <div className="space-y-2 ml-11">
                {question.options?.map((option) => {
                  const selected = Array.isArray(answers[question.id])
                    ? (answers[question.id] as string[]).includes(option.id)
                    : answers[question.id] === option.id

                  return (
                    <button
                      key={option.id}
                      onClick={() => handleSelect(question.id, option.id, question.type)}
                      disabled={answered}
                      className={`w-full text-left px-4 py-3 rounded-lg border transition-colors ${
                        selected
                          ? 'border-primary-500 bg-primary-50 text-primary-800'
                          : 'border-slate-200 hover:border-primary-300 hover:bg-slate-50'
                      } ${answered ? 'cursor-default' : 'cursor-pointer'}`}
                    >
                      <span className="font-medium mr-2">{option.id}.</span>
                      {option.text}
                    </button>
                  )
                })}
              </div>
            )}

            {!answered ? (
              <div className="mt-4 ml-11">
                <button
                  onClick={() => handleSubmit(question.id)}
                  disabled={!answers[question.id] || (Array.isArray(answers[question.id]) && (answers[question.id] as string[]).length === 0)}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors"
                >
                  提交答案
                </button>
              </div>
            ) : (
              <div className="mt-4 ml-11">
                <div className="flex items-center gap-2 mb-2">
                  {correct ? (
                    <>
                      <CheckCircle2 size={20} className="text-success" />
                      <span className="font-semibold text-success">回答正确</span>
                    </>
                  ) : (
                    <>
                      <XCircle size={20} className="text-danger" />
                      <span className="font-semibold text-danger">回答错误</span>
                    </>
                  )}
                </div>
                <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-lg p-3">
                  <Lightbulb size={18} className="text-warning shrink-0 mt-0.5" />
                  <p className="text-sm text-slate-700">{question.explanation}</p>
                </div>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
