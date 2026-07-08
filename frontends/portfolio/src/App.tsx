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
import SplashOverlay from './components/SplashOverlay'

const MUSIC_SRC = '/music/shattered-dream.mp3'
const MUSIC_VOLUME = 0.5
const MUSIC_MUTED_KEY = 'kairos-music-muted'

function DemoRoute({ slug, src }: { slug: string; src: string }) {
  return <Demo slug={slug} src={src} />
}

function getInitialUserMuted(): boolean {
  if (typeof window === 'undefined') return false
  return window.localStorage.getItem(MUSIC_MUTED_KEY) === 'true'
}

export default function App() {
  const { pathname } = useLocation()
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [userMuted, setUserMuted] = useState(getInitialUserMuted)
  const [isPlaying, setIsPlaying] = useState(false)

  // Initialize audio and attempt autoplay unless user has muted
  useEffect(() => {
    const audio = new Audio(MUSIC_SRC)
    audio.loop = true
    audio.volume = MUSIC_VOLUME
    audioRef.current = audio

    if (!userMuted) {
      audio
        .play()
        .then(() => setIsPlaying(true))
        .catch(() => {
          // Browser blocked autoplay; wait for first user interaction
          setIsPlaying(false)
        })
    }

    return () => {
      audio.pause()
      audio.src = ''
      audioRef.current = null
    }
  }, [userMuted])

  // Resume audio on first user interaction if autoplay was blocked
  useEffect(() => {
    if (userMuted) return

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
  }, [userMuted])

  const handleMusicToggle = () => {
    const audio = audioRef.current
    if (!audio) return

    if (userMuted) {
      // User wants to unmute
      audio
        .play()
        .then(() => {
          setIsPlaying(true)
          setUserMuted(false)
          localStorage.setItem(MUSIC_MUTED_KEY, 'false')
        })
        .catch(() => {})
    } else {
      // User wants to mute
      audio.pause()
      setIsPlaying(false)
      setUserMuted(true)
      localStorage.setItem(MUSIC_MUTED_KEY, 'true')
    }
  }

  return (
    <>
      <SplashOverlay />
      <div className="min-h-screen bg-base">
        <NavBar isMuted={userMuted} onMusicToggle={handleMusicToggle} />
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
