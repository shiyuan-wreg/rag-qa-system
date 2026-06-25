import { Routes, Route, useLocation } from 'react-router-dom'
import NavBar from './components/NavBar'
import Home from './pages/Home'
import Demo from './pages/Demo'
import Learn from './pages/Learn'
import Me from './pages/Me'
import Changelog from './pages/Changelog'
import PageTransition from './components/PageTransition'

function DemoRoute({ slug, src }: { slug: string; src: string }) {
  return <Demo slug={slug} src={src} />
}

export default function App() {
  const { pathname } = useLocation()

  return (
    <div className="min-h-screen bg-base">
      <NavBar />
      <PageTransition key={pathname}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/rag" element={<DemoRoute slug="rag" src="/rag/" />} />
          <Route path="/fc" element={<DemoRoute slug="fc" src="/fc/" />} />
          <Route path="/nexus" element={<DemoRoute slug="nexus" src="/nexus/" />} />
          <Route path="/learn" element={<Learn />} />
          <Route path="/doctomd" element={<DemoRoute slug="doctomd" src="/doctomd/" />} />
          <Route path="/iconforge" element={<DemoRoute slug="iconforge" src="/iconforge/" />} />
          <Route path="/changelog" element={<Changelog />} />
          <Route path="/me" element={<Me />} />
        </Routes>
      </PageTransition>
    </div>
  )
}
