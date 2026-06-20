/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        canvas: { DEFAULT: '#ffffff', warm: '#f7f6f3', soft: '#f6f5f4' },
        surface: '#ffffff',
        border: '#e6e6e6',
        ink: '#37352f',
        muted: '#615d59',
        tertiary: '#9a9aa1',
        accent: { DEFAULT: '#0075de', soft: 'rgba(0,117,222,0.10)' },
        danger: { DEFAULT: '#dd5b00', soft: 'rgba(221,91,0,0.10)' },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Lora', 'Georgia', 'ui-serif', 'serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      borderRadius: {
        card: '12px',
        input: '6px',
      },
      boxShadow: {
        sm: '0 1px 2px rgba(0,0,0,0.04)',
        md: '0 8px 24px rgba(0,0,0,0.10)',
        lg: '0 16px 40px rgba(0,0,0,0.16)',
      },
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-400px 0' },
          '100%': { backgroundPosition: '400px 0' },
        },
        'toast-in': {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        shimmer: 'shimmer 1.4s infinite linear',
        'toast-in': 'toast-in 0.18s ease-out',
      },
    },
  },
  plugins: [],
}
