import { useMotionPreference } from '../hooks/useMotionPreference'

export default function ParallaxToggle() {
  const { parallaxEnabled, setParallaxEnabled, prefersReducedMotion } = useMotionPreference()
  const disabled = prefersReducedMotion
  const on = parallaxEnabled && !disabled

  return (
    <button
      type="button"
      role="switch"
      aria-checked={on}
      aria-label="3D 悬浮视差"
      onClick={() => setParallaxEnabled(!parallaxEnabled)}
      disabled={disabled}
      title={disabled ? '系统已开启“减少动态效果”,3D 视差已禁用' : '切换 3D 悬浮视差'}
      className={[
        'inline-flex items-center gap-1.5 select-none transition-opacity',
        disabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer',
      ].join(' ')}
    >
      <span className="text-[10px] font-semibold tracking-widest text-tertiary">3D</span>
      <span
        className={[
          'relative w-8 h-4 rounded-full border transition-colors duration-200',
          on ? 'bg-accent border-accent' : 'bg-surface border-border',
        ].join(' ')}
      >
        <span
          className={[
            'absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full transition-all duration-200',
            on ? 'left-[18px] bg-accent-text' : 'left-0.5 bg-tertiary',
          ].join(' ')}
        />
      </span>
    </button>
  )
}
