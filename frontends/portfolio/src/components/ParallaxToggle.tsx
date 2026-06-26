import { useMotionPreference } from '../hooks/useMotionPreference'

export default function ParallaxToggle() {
  const { parallaxEnabled, setParallaxEnabled, prefersReducedMotion } = useMotionPreference()
  const disabled = prefersReducedMotion

  return (
    <button
      onClick={() => setParallaxEnabled(!parallaxEnabled)}
      disabled={disabled}
      aria-pressed={parallaxEnabled && !disabled}
      title={disabled ? '系统已开启“减少动态效果”,3D 视差已禁用' : '切换 3D 悬浮视差'}
      className={[
        'inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-md border transition-all',
        disabled
          ? 'border-border text-muted opacity-50 cursor-not-allowed'
          : parallaxEnabled
            ? 'border-accent bg-accent text-accent-text shadow-sm'
            : 'border-border text-tertiary hover:text-primary hover:bg-surface-hover',
      ].join(' ')}
    >
      3D
    </button>
  )
}
