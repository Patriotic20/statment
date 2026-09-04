import type { ApiResult } from './api/client'

/** Достаёт человекочитаемое сообщение об ошибке из ответа API. */
export function errorMessage(r: ApiResult, fallback = 'So\'rovda xatolik'): string {
  const data = r.data
  if (data && typeof data === 'object' && 'detail' in data) {
    const d = (data as { detail: unknown }).detail
    return typeof d === 'string' ? d : JSON.stringify(d)
  }
  return `${fallback} (${r.status})`
}

/** Дата и время в привычном виде: 04.09.2026 16:52.
 *  Формат собираем вручную — Intl с разными локалями браузера даёт то
 *  «9/4/2026, 4:52 PM», то «2026-09-04», а нужен один вид для всех. */
export function formatDateTime(value: string): string {
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return '—'
  const p = (n: number) => String(n).padStart(2, '0')
  return `${p(d.getDate())}.${p(d.getMonth() + 1)}.${d.getFullYear()} ${p(d.getHours())}:${p(d.getMinutes())}`
}
