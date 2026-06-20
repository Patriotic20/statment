export function ErrorBanner({ message }: { message?: string }) {
  if (!message) return null
  return (
    <div className="mb-4 rounded-input border border-danger/30 bg-danger-soft px-4 py-2.5 text-sm text-danger">
      {message}
    </div>
  )
}
