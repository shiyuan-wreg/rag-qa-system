import { useState } from 'react'
import { Copy, Check, Play, Lightbulb } from 'lucide-react'
import type { CodeLab } from '../types/course'

interface CodeLabProps {
  lab: CodeLab
}

export default function CodeLab({ lab }: CodeLabProps) {
  const [code, setCode] = useState(lab.starterCode)
  const [copied, setCopied] = useState(false)
  const [showHint, setShowHint] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
      <div className="bg-slate-50 border-b border-slate-200 px-4 py-3 flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-slate-900">{lab.title}</h3>
          <p className="text-sm text-slate-500">{lab.description}</p>
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-slate-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
        >
          {copied ? <Check size={16} /> : <Copy size={16} />}
          {copied ? '已复制' : '复制代码'}
        </button>
      </div>

      <div className="p-4">
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          className="w-full h-64 font-mono text-sm bg-slate-900 text-slate-100 p-4 rounded-lg resize-y focus:outline-none focus:ring-2 focus:ring-primary-500"
          spellCheck={false}
        />

        {lab.expectedOutput && (
          <div className="mt-3 text-sm text-slate-600">
            <span className="font-medium">预期输出：</span>
            <code className="bg-slate-100 px-2 py-0.5 rounded ml-1">{lab.expectedOutput}</code>
          </div>
        )}

        {lab.hint && (
          <div className="mt-3">
            <button
              onClick={() => setShowHint(!showHint)}
              className="flex items-center gap-1.5 text-sm text-amber-600 hover:text-amber-700 font-medium"
            >
              <Lightbulb size={16} />
              {showHint ? '隐藏提示' : '查看提示'}
            </button>
            {showHint && (
              <div className="mt-2 p-3 bg-amber-50 border border-amber-200 rounded-lg text-sm text-slate-700">
                {lab.hint}
              </div>
            )}
          </div>
        )}

        <div className="mt-4 flex items-center gap-3">
          <button
            onClick={() => window.open('https://www.programiz.com/python-programming/online-compiler/', '_blank')}
            className="flex items-center gap-1.5 px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors"
          >
            <Play size={16} />
            在线运行
          </button>
          <span className="text-sm text-slate-500">
            点击后在浏览器中打开在线 Python 编译器运行代码
          </span>
        </div>
      </div>
    </div>
  )
}
