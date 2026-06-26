import { WORKS } from '../data/works'
import DemoFrame from '../components/DemoFrame'
import DemoInfoCard from '../components/DemoInfoCard'
import SidebarLayout from '../components/SidebarLayout'
import SidebarNav from '../components/SidebarNav'
import type { SidebarNavItem } from '../components/SidebarNav'
import PageTransition from '../components/PageTransition'
import MachineSkin from '../components/MachineSkin'
import { useTheme } from '../hooks/useTheme'

export default function Demo({ slug, src }: { slug: string; src: string }) {
  const { theme } = useTheme()
  const work = WORKS.find((w) => w.slug === slug)!
  const navItems: SidebarNavItem[] = WORKS.filter((w) => w.slug !== 'learn').map((w) => ({
    key: w.slug,
    to: w.path,
    label: w.title,
    icon: w.icon,
  }))

  const content = (
    <div className="max-w-wide mx-auto w-full px-4 sm:px-6 lg:px-8 py-4 flex-1 min-h-0">
      <SidebarLayout
        sidebar={
          <div className="space-y-5">
            <div>
              <div className="text-xs font-semibold text-muted uppercase tracking-wider mb-3 px-3">
                作品导航
              </div>
              <SidebarNav items={navItems} activeKey={slug} />
            </div>
            <DemoInfoCard work={work} />
          </div>
        }
      >
        <DemoFrame src={src} title={work.title} index={work.index} />
      </SidebarLayout>
    </div>
  )

  const machine = theme === 'machine'

  return (
    <PageTransition>
      <div className="h-[calc(100vh-3.5rem)] flex flex-col">
        {machine ? <MachineSkin>{content}</MachineSkin> : content}
      </div>
    </PageTransition>
  )
}
