import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { createApi, type Api } from '../api/endpoints'

interface AuthContextValue {
  token: string
  baseUrl: string
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<{ ok: boolean; error?: string }>
  logout: () => void
  /** Типизированный API-клиент с подставленными baseUrl/token. */
  api: Api
}

const AuthContext = createContext<AuthContextValue | null>(null)

const TOKEN_KEY = 'rrtm_token'
// По умолчанию — относительный путь: запросы идут на тот же origin и
// проксируются nginx (`/api/` → backend:8000). Работает на любом хосте/порте.
// Для локального `npm run dev` переопределяется через VITE_API_URL в .env.
const BASE_URL = import.meta.env.VITE_API_URL || '/api'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY) || '')

  const logout = useCallback(() => {
    setToken('')
    localStorage.removeItem(TOKEN_KEY)
  }, [])

  // Базовый клиент без токена — для логина.
  const api = useMemo(() => createApi({ baseUrl: BASE_URL, token }), [token])

  const login = useCallback(async (username: string, password: string) => {
    const r = await createApi({ baseUrl: BASE_URL }).login(username, password)
    if (r.ok && r.data?.access_token) {
      setToken(r.data.access_token)
      localStorage.setItem(TOKEN_KEY, r.data.access_token)
      return { ok: true }
    }
    const detail =
      r.data && typeof r.data === 'object' && 'detail' in r.data
        ? String((r.data as { detail: unknown }).detail)
        : 'Noto\'g\'ri login yoki parol'
    return { ok: false, error: detail }
  }, [])

  const value = useMemo(
    () => ({ token, baseUrl: BASE_URL, isAuthenticated: !!token, login, logout, api }),
    [token, login, logout, api],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
