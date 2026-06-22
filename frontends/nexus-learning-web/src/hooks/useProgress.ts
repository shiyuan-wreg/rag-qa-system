import { useState, useEffect, useCallback } from 'react'
import type { Progress } from '../types/course'

const STORAGE_KEY = 'nexus-learning-progress'

export function useProgress() {
  const [progress, setProgress] = useState<Progress>({
    completedLessons: [],
    quizResults: {},
    wrongQuestions: [],
  })
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      try {
        setProgress(JSON.parse(saved))
      } catch (e) {
        console.error('Failed to load progress:', e)
      }
    }
    setLoaded(true)
  }, [])

  useEffect(() => {
    if (loaded) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(progress))
    }
  }, [progress, loaded])

  const completeLesson = useCallback((lessonId: string) => {
    setProgress(prev => ({
      ...prev,
      completedLessons: prev.completedLessons.includes(lessonId)
        ? prev.completedLessons
        : [...prev.completedLessons, lessonId],
    }))
  }, [])

  const recordQuizResult = useCallback((lessonId: string, correct: number, total: number) => {
    setProgress(prev => ({
      ...prev,
      quizResults: {
        ...prev.quizResults,
        [lessonId]: { correct, total },
      },
    }))
  }, [])

  const addWrongQuestion = useCallback((questionId: string) => {
    setProgress(prev => ({
      ...prev,
      wrongQuestions: prev.wrongQuestions.includes(questionId)
        ? prev.wrongQuestions
        : [...prev.wrongQuestions, questionId],
    }))
  }, [])

  const removeWrongQuestion = useCallback((questionId: string) => {
    setProgress(prev => ({
      ...prev,
      wrongQuestions: prev.wrongQuestions.filter(id => id !== questionId),
    }))
  }, [])

  const resetProgress = useCallback(() => {
    setProgress({
      completedLessons: [],
      quizResults: {},
      wrongQuestions: [],
    })
  }, [])

  return {
    progress,
    loaded,
    completeLesson,
    recordQuizResult,
    addWrongQuestion,
    removeWrongQuestion,
    resetProgress,
  }
}
