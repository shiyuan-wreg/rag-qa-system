export default function Me() {
  return (
    <div className="max-w-3xl mx-auto p-6 space-y-6">
      <section>
        <h2 className="text-xl font-bold mb-2">技能栈</h2>
        <p className="text-gray-600">Python · FastAPI · RAG · LangChain · React · Docker · AI/Agent 工程</p>
      </section>
      <section>
        <h2 className="text-xl font-bold mb-2">简历</h2>
        <a href="/resume.pdf" className="text-blue-600 underline" target="_blank" rel="noopener noreferrer">下载简历（PDF）</a>
      </section>
      <section>
        <h2 className="text-xl font-bold mb-2">项目</h2>
        <ul className="list-disc pl-5 text-gray-600 space-y-1">
          <li><a href="/quiz/" className="text-blue-600 underline" target="_blank" rel="noopener noreferrer">cs-quiz-app 面试题库（待集成）</a></li>
        </ul>
      </section>
    </div>
  )
}
