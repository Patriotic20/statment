/** Кружок с инициалами из ФИО. */
export function Avatar({ name }: { name: string }) {
  const initials = name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase() ?? '')
    .join('')

  return (
    <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-canvas-soft text-xs font-semibold text-muted">
      {initials || '?'}
    </span>
  )
}
