import type { ReactNode } from 'react'

type Tone = 'neutral' | 'accent' | 'mono' | 'danger'

const tones: Record<Tone, string> = {
  neutral: 'bg-canvas-soft text-muted border border-border',
  accent: 'bg-accent-soft text-accent',
  mono: 'bg-canvas-soft text-muted font-mono border border-border',
  danger: 'bg-danger-soft text-danger',
}

export function Badge({
  children,
  tone = 'neutral',
}: {
  children: ReactNode
  tone?: Tone
}) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${tones[tone]}`}
    >
      {children}
    </span>
  )
}
