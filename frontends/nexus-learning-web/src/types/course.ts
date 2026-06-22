export interface QuizOption {
  id: string
  text: string
}

export interface QuizQuestion {
  id: string
  type: 'single' | 'multiple' | 'code'
  question: string
  options?: QuizOption[]
  correctAnswer: string | string[]
  explanation: string
  code?: string
}

export interface CodeLab {
  id: string
  title: string
  description: string
  starterCode: string
  expectedOutput?: string
  hint?: string
}

export interface Lesson {
  id: string
  moduleId: string
  moduleTitle: string
  order: number
  title: string
  description: string
  objectives: string[]
  prerequisites: string[]
  keyConcepts: string[]
  content: string
  codeLabs: CodeLab[]
  quizzes: QuizQuestion[]
  commonMistakes: string[]
  furtherReading: { title: string; url?: string }[]
  checklist: string[]
}

export interface Module {
  id: string
  title: string
  description: string
  order: number
  lessons: Lesson[]
}

export interface Progress {
  completedLessons: string[]
  quizResults: Record<string, { correct: number; total: number }>
  wrongQuestions: string[]
}
