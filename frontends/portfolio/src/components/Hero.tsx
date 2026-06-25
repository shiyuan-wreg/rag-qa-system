import { Link } from 'react-router-dom'
import GlitchTitle from './GlitchTitle'
import Typewriter from './Typewriter'
import FakeTerminal from './FakeTerminal'
import Button from './Button'

export default function Hero() {
  return (
    <section className="hero-ambient relative overflow-hidden bg-hero border-b border-border-subtle">
      <div className="relative max-w-content mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28 text-center">
        <p className="font-mono text-xs tracking-[0.2em] uppercase text-tertiary mb-6">个人集成学习网站 · Personal Lab</p>
        <GlitchTitle text="构建可运行的 AI / Agent 应用" />
        <Typewriter
          text="RAG · Function-Calling · Multi-Agent · 已部署生产环境"
          className="block mt-6 text-sm md:text-base text-secondary"
        />
        <div className="mt-9 flex items-center justify-center gap-3">
          <Link to="/rag"><Button>浏览作品</Button></Link>
          <Link to="/learn"><Button variant="secondary">开始学习</Button></Link>
        </div>
        <div className="mt-12">
          <FakeTerminal lines={[
            { type: 'cmd', text: 'curl https://www.shiyuan-wreg.cloud/rag/api/ask' },
            { type: 'out', text: '→ 200 OK · 检索 4 段 · 生成回答 (1.2s)' },
            { type: 'cmd', text: 'docker compose ps' },
            { type: 'out', text: 'rag ✓  fc ✓  nexus ✓  doctomd ✓  nginx ✓' },
          ]} />
        </div>
      </div>
    </section>
  )
}
