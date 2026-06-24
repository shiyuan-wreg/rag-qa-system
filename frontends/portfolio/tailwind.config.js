/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        base: 'var(--bg-base)',
        soft: 'var(--bg-soft)',
        surface: {
          DEFAULT: 'var(--surface-default)',
          raised: 'var(--surface-raised)',
          hover: 'var(--surface-hover)',
          soft: 'var(--surface-soft)',
        },
        border: {
          DEFAULT: 'var(--border-default)',
          subtle: 'var(--border-subtle)',
        },
        primary: 'var(--text-primary)',
        secondary: 'var(--text-secondary)',
        tertiary: 'var(--text-tertiary)',
        muted: 'var(--text-muted)',
        link: 'var(--text-link)',
        accent: {
          DEFAULT: 'var(--accent-primary)',
          text: 'var(--accent-primary-text)',
          secondary: {
            bg: 'var(--accent-secondary-bg)',
            text: 'var(--accent-secondary-text)',
          },
        },
      },
      backgroundImage: {
        hero: 'var(--bg-hero)',
      },
      boxShadow: {
        sm: 'var(--shadow-sm)',
        md: 'var(--shadow-md)',
        lg: 'var(--shadow-lg)',
        glow: 'var(--shadow-glow)',
      },
      borderRadius: {
        sm: 'var(--radius-sm)',
        md: 'var(--radius-md)',
        lg: 'var(--radius-lg)',
        xl: 'var(--radius-xl)',
        full: 'var(--radius-full)',
      },
      spacing: {
        18: '4.5rem',
        22: '5.5rem',
      },
      maxWidth: {
        content: 'var(--max-content)',
        wide: 'var(--max-wide)',
      },
      fontFamily: {
        sans: 'var(--font-sans)',
        mono: 'var(--font-mono)',
      },
    },
  },
  plugins: [],
}
