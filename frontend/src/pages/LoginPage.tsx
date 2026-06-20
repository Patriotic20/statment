import { useState, type FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Button } from '../components/ui/Button'
import { Field, Input } from '../components/ui/Field'
import { ErrorBanner } from '../components/ErrorBanner'

export function LoginPage() {
  const { login, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (isAuthenticated) return <Navigate to="/faculties" replace />

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    const r = await login(username.trim(), password)
    setLoading(false)
    if (r.ok) navigate('/faculties', { replace: true })
    else setError(r.error || 'Kirishda xatolik')
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-canvas-warm px-4">
      <div className="w-full max-w-sm rounded-card border border-border bg-surface p-8 shadow-sm">
        <div className="mb-7 flex flex-col items-center gap-3">
          <span className="grid h-12 w-12 place-items-center rounded-card bg-accent text-xl font-bold text-white">
            R
          </span>
          <div className="text-center">
            <h1 className="text-2xl font-semibold text-ink">RRTM ga kirish</h1>
            <p className="mt-1 text-sm text-muted">Inventar va xodimlarni boshqarish</p>
          </div>
        </div>
        <ErrorBanner message={error} />
        <form onSubmit={handleSubmit} className="space-y-4">
          <Field label="Foydalanuvchi nomi">
            <Input
              value={username}
              autoComplete="username"
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </Field>
          <Field label="Parol">
            <Input
              type="password"
              value={password}
              autoComplete="current-password"
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </Field>
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? 'Kirish...' : 'Kirish'}
          </Button>
        </form>
      </div>
    </div>
  )
}
