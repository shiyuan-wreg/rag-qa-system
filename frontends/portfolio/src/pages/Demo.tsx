import { WORKS } from '../data/works'
import DemoFrame from '../components/DemoFrame'
import DemoInfoCard from '../components/DemoInfoCard'
import SidebarLayout from '../components/SidebarLayout'
import SidebarNav from '../components/SidebarNav'
import type { SidebarNavItem } from '../components/SidebarNav'
import PageChangelog from '../components/PageChangelog'
import PageTransition from '../components/PageTransition'

export default function Demo({ slug, src }: { slug: string; src: string }) {
  const work = WORKS.find((w) => w.slug === slug)!
  const navItems: SidebarNavItem[] = WORKS.filter((w) => w.slug !== 'learn').map((w) => ({
    key: w.slug,
    to: w.path,
    label: w.title,
    icon: w.icon,
  }))

  return (
    <PageTransition>
      <PageChangelog pageKey={slug} />
      <SidebarLayout
        sidebar={
          <div>
            <div className="text-xs font-semibold text-muted uppercase tracking-wider mb-3 px-3">
              作品导航
            </div>
            <SidebarNav items={navItems} activeKey={slug} />
          </div>
        }
      >
        <div className="space-y-4">
          <DemoInfoCard work={work} />
          <DemoFrame src={src} title={work.title} />
        </div>
      </SidebarLayout>
    </PageTransition>
  )
}
