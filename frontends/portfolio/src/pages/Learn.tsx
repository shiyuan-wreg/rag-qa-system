import DemoFrame from '../components/DemoFrame'
import SidebarLayout from '../components/SidebarLayout'
import SidebarNav from '../components/SidebarNav'
import PageChangelog from '../components/PageChangelog'
import PageTransition from '../components/PageTransition'
import { LEARN_NAV } from '../data/learnNav'

export default function Learn() {
  const navItems = LEARN_NAV.flatMap((m) => [
    { key: m.id, to: `/learn/#${m.id}`, label: m.title },
    ...m.lessons.map((l) => ({
      key: l.id,
      to: `/learn/#${l.id}`,
      label: l.title,
    })),
  ])

  return (
    <PageTransition>
      <PageChangelog pageKey="learn" />
      <SidebarLayout
        sidebar={
          <div>
            <div className="text-xs font-semibold text-muted uppercase tracking-wider mb-3 px-3">
              课程目录
            </div>
            <SidebarNav items={navItems} activeKey="learn" />
          </div>
        }
      >
        <DemoFrame src="/learn/" title="Nexus 交互式学习站" />
      </SidebarLayout>
    </PageTransition>
  )
}
