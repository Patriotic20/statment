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
