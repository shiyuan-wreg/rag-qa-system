import { WORKS } from '../data/works'
import DemoFrame from '../components/DemoFrame'

export default function Demo({ slug, src }: { slug: string; src: string }) {
  const work = WORKS.find((w) => w.slug === slug)!
  return <DemoFrame work={work} src={src} />
}
