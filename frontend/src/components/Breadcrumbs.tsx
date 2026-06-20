import { Fragment } from 'react'
import { ChevronRight } from 'lucide-react'
import { Link } from 'react-router-dom'

export interface Crumb {
  label: string
  to?: string
}

export function Breadcrumbs({ items }: { items: Crumb[] }) {
  return (
    <nav className="mb-4 flex flex-wrap items-center gap-1 text-sm text-muted">
      {items.map((c, i) => (
        <Fragment key={i}>
          {i > 0 && <ChevronRight size={14} className="text-tertiary" />}
          {c.to ? (
            <Link to={c.to} className="transition hover:text-accent">
              {c.label}
            </Link>
          ) : (
            <span className="font-medium text-ink">{c.label}</span>
          )}
        </Fragment>
      ))}
    </nav>
  )
}
