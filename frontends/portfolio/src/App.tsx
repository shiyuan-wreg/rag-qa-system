import { useEffect, useRef, useState } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom'
import NavBar from './components/NavBar'
import Home from './pages/Home'
import Demo from './pages/Demo'
import Learn from './pages/Learn'
import Me from './pages/Me'
import Changelog from './pages/Changelog'
import PageTransition from './components/PageTransition'
import GlobalHud from './components/GlobalHud'
import ParallaxViewport from './components/ParallaxViewport'
import SplashOverlay, { TOTAL_SPLASH_MS } from './components/SplashOverlay'

const MUSIC_SRC = '/music/shattered-dream.mp3'
const MUSIC_VOLUME = 0.5

function DemoRoute({ slug, src }: { slug: string; src: string }) {
  return <Demo slug={slug} src={src} />
}

export default function App() {
  const { pathname } = useLocation()
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [splashDone, setSplashDone] = useState(false)

  // Initialize audio and attempt autoplay
  useEffect(() => {
    const audio = new Audio(MUSIC_SRC)
    audio.loop = true
    audio.volume = MUSIC_VOLUME
    audioRef.current = audio

    audio
      .play()
      .then(() => setIsPlaying(true))
      .catch(() => {
        // Browser blocked autoplay; wait for first user interaction
        setIsPlaying(false)
      })

    return () => {
      audio.pause()
      audio.src = ''
      audioRef.current = null
    }
  }, [])

  // Resume audio on first user interaction if autoplay was blocked
  useEffect(() => {
    if (isMuted) return

    const tryResume = () => {
      const audio = audioRef.current
      if (audio && audio.paused) {
        audio.play().then(() => setIsPlaying(true)).catch(() => {})
      }
    }

    window.addEventListener('click', tryResume, { once: true })
    window.addEventListener('keydown', tryResume, { once: true })

    return () => {
      window.removeEventListener('click', tryResume)
      window.removeEventListener('keydown', tryResume)
    }
  }, [isMuted])

  // Splash overlay lifecycle
  useEffect(() => {
    const timer = window.setTimeout(() => setSplashDone(true), TOTAL_SPLASH_MS)
    return () => window.clearTimeout(timer)
  }, [])

  const handleMusicToggle = () => {
    const audio = audioRef.current
    if (!audio) return

    if (isPlaying) {
      audio.pause()
      setIsPlaying(false)
      setIsMuted(true)
    } else {
      audio
        .play()
        .then(() => {
          setIsPlaying(true)
          setIsMuted(false)
        })
        .catch(() => {})
    }
  }

  return (
    <>
      <SplashOverlay />
      <div
        className={`min-h-screen bg-base transition-opacity ease-out ${
          splashDone ? 'opacity-100' : 'opacity-0'
        }`}
        style={{ transitionDuration: `${TOTAL_SPLASH_MS}ms` }}
      >
        <NavBar isPlaying={isPlaying} onMusicToggle={handleMusicToggle} />
        <ParallaxViewport>
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
        </ParallaxViewport>
        <GlobalHud />
      </div>
    </>
  )
}
