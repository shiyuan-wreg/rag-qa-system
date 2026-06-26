import DemoFrame from '../components/DemoFrame'
import PageTransition from '../components/PageTransition'
import MachineSkin from '../components/MachineSkin'
import { useTheme } from '../hooks/useTheme'

export default function Learn() {
  const { theme } = useTheme()
  const content = (
    <div className="flex-1 min-h-0 px-4 sm:px-6 lg:px-8 py-4">
      <DemoFrame src="/learn/" title="Nexus 交互式学习站" />
    </div>
  )
  return (
    <PageTransition>
      <div className="h-[calc(100vh-3.5rem)] flex flex-col">
        {theme === 'machine' ? <MachineSkin>{content}</MachineSkin> : content}
      </div>
    </PageTransition>
  )
}
