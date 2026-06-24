import DemoFrame from '../components/DemoFrame'
import PageTransition from '../components/PageTransition'

export default function Learn() {
  return (
    <PageTransition>
      <div className="h-[calc(100vh-3.5rem)] flex flex-col">
        <div className="flex-1 min-h-0 px-4 sm:px-6 lg:px-8 py-4">
          <DemoFrame src="/learn/" title="Nexus 交互式学习站" />
        </div>
      </div>
    </PageTransition>
  )
}
