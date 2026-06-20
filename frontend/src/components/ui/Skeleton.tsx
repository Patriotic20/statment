/** Серия скелет-карточек на время загрузки списка. */
export function SkeletonCards({ count = 6 }: { count?: number }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="rounded-card border border-border bg-surface p-5 shadow-sm">
          <div className="skeleton h-3 w-20" />
          <div className="skeleton mt-3 h-5 w-3/4" />
          <div className="skeleton mt-4 h-3 w-24" />
        </div>
      ))}
    </div>
  )
}

/** Скелет-строки для списков (сотрудники/инвентарь). */
export function SkeletonRows({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="rounded-card border border-border bg-surface p-4 shadow-sm">
          <div className="skeleton h-4 w-1/2" />
          <div className="skeleton mt-2 h-3 w-2/3" />
        </div>
      ))}
    </div>
  )
}
