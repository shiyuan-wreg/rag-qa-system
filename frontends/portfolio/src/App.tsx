import { Routes, Route } from 'react-router-dom'
import NavBar from './components/NavBar'
import Home from './pages/Home'
import Demo from './pages/Demo'
import Learn from './pages/Learn'
import Me from './pages/Me'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/rag" element={<Demo slug="rag" src="/rag/" />} />
        <Route path="/fc" element={<Demo slug="fc" src="/fc/" />} />
        <Route path="/nexus" element={<Demo slug="nexus" src="/nexus/" />} />
        <Route path="/learn" element={<Learn />} />
        <Route path="/me" element={<Me />} />
      </Routes>
    </div>
  )
}
