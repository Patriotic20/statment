import { CheckCircle2, X, AlertCircle } from 'lucide-react'
import { useToast } from '../context/ToastContext'

export function Toaster() {
  const { toasts, dismiss } = useToast()

  return (
    <div className="pointer-events-none fixed bottom-5 right-5 z-50 flex w-full max-w-sm flex-col gap-2">
      {toasts.map((t) => (
        <div
          key={t.id}
          className="pointer-events-auto flex items-start gap-3 rounded-card border border-border bg-surface p-3.5 shadow-lg animate-toast-in"
        >
          <span className={t.tone === 'success' ? 'text-accent' : 'text-danger'}>
            {t.tone === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
          </span>
          <p className="flex-1 text-sm text-ink">{t.message}</p>
          <button
            onClick={() => dismiss(t.id)}
            className="text-tertiary transition hover:text-ink"
            aria-label="Yopish"
          >
            <X size={16} />
          </button>
        </div>
      ))}
    </div>
  )
}
