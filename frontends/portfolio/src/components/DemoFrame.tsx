import { Work } from '../data/works'

export default function DemoFrame({ work, src }: { work: Work; src: string }) {
  return (
    <div className="flex flex-col lg:flex-row gap-4 p-6">
      <iframe title={work.title} src={src}
        className="flex-1 min-h-[70vh] border rounded-lg" />
      <aside className="lg:w-80 shrink-0 space-y-3">
        <h2 className="text-xl font-bold">{work.title}</h2>
        <p className="text-gray-600">{work.desc}</p>
        <div className="flex flex-wrap gap-2">
          {work.tech.map((t) => (
            <span key={t} className="px-2 py-1 text-xs bg-gray-100 rounded">{t}</span>
          ))}
        </div>
        {work.github && (
          <a href={work.github} className="text-blue-600 underline" target="_blank">查看源码</a>
        )}
      </aside>
    </div>
  )
}
