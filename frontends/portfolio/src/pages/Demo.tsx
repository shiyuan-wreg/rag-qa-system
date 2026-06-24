import { WORKS } from '../data/works'
import DemoFrame from '../components/DemoFrame'
import DemoInfoCard from '../components/DemoInfoCard'

export default function Demo({ slug, src }: { slug: string; src: string }) {
  const work = WORKS.find((w) => w.slug === slug)!
  return (
    <div className="flex flex-col lg:flex-row gap-4 p-6">
      <DemoFrame src={src} title={work.title} />
      <aside className="lg:w-80 shrink-0">
        <DemoInfoCard work={work} />
      </aside>
    </div>
  )
}
