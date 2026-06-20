export interface ApiResult<T = unknown> {
  ok: boolean
  status: number | string
  data: T | null
}

export interface RequestEntry {
  method: string
  path: string
  status: number | string
  text: string
  ok: boolean
}

interface ApiOptions {
  baseUrl: string
  token?: string
  /** Тело запроса: JSON-объект или, для логина, пары form-urlencoded. */
  body?: Record<string, unknown>
  /** true → отправить тело как application/x-www-form-urlencoded. */
  form?: boolean
  /** Колбэк логирования каждого запроса/ответа. */
  onLog?: (entry: RequestEntry) => void
}

/**
 * Единая обёртка над fetch: подставляет baseUrl и Authorization,
 * выбирает form/JSON, логирует результат и вытаскивает detail при ошибке.
 */
export async function apiRequest<T = unknown>(
  method: string,
  path: string,
  opts: ApiOptions,
): Promise<ApiResult<T>> {
  const { baseUrl, token, body, form, onLog } = opts
  const url = baseUrl.replace(/\/+$/, '') + path

  const headers: Record<string, string> = {}
  if (token) headers['Authorization'] = 'Bearer ' + token

  let payload: string | undefined
  if (body !== undefined) {
    if (form) {
      headers['Content-Type'] = 'application/x-www-form-urlencoded'
      payload = new URLSearchParams(body as Record<string, string>).toString()
    } else {
      headers['Content-Type'] = 'application/json'
      payload = JSON.stringify(body)
    }
  }

  let res: Response
  try {
    res = await fetch(url, { method, headers, body: payload })
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e)
    onLog?.({ method, path, status: '—', text: 'NETWORK ERROR: ' + msg, ok: false })
    return { ok: false, status: '—', data: null }
  }

  const raw = await res.text()
  let data: unknown = null
  try {
    data = raw ? JSON.parse(raw) : null
  } catch {
    data = raw
  }

  let text = typeof data === 'string' ? data : JSON.stringify(data, null, 2)
  if (!res.ok && data && typeof data === 'object' && 'detail' in data) {
    text = 'detail: ' + JSON.stringify((data as { detail: unknown }).detail, null, 2)
  }

  onLog?.({ method, path, status: res.status, text: text || '(пусто)', ok: res.ok })
  return { ok: res.ok, status: res.status, data: data as T }
}
