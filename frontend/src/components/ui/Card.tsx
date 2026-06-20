import type { ReactNode } from 'react'

interface CardProps {
  children: ReactNode
  className?: string
  onClick?: () => void
}

export function Card({ children, className = '', onClick }: CardProps) {
  return (
    <div
      onClick={onClick}
      className={`rounded-card border border-border bg-surface p-5 shadow-sm transition ${
        onClick
          ? 'cursor-pointer hover:-translate-y-0.5 hover:border-accent/40 hover:shadow-md'
          : ''
      } ${className}`}
    >
      {children}
    </div>
  )
}
