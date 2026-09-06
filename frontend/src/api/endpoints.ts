import { apiRequest, type ApiResult, type RequestEntry } from './client'
import type { Faculty, Room, Employee, Inventory, Token, Issue, IssueStatus, User } from '../types'

export interface CallConfig {
  baseUrl: string
  token?: string
  onLog?: (entry: RequestEntry) => void
}

/**
 * Фабрика типизированных хелперов поверх apiRequest.
 * Создаётся в AuthContext с актуальными baseUrl/token.
 */
export function createApi(cfg: CallConfig) {
  const req = <T>(
    method: string,
    path: string,
    opts?: { body?: Record<string, unknown>; form?: boolean },
  ): Promise<ApiResult<T>> =>
    apiRequest<T>(method, path, {
      baseUrl: cfg.baseUrl,
      token: cfg.token,
      onLog: cfg.onLog,
      body: opts?.body,
      form: opts?.form,
    })

  return {
    health: () => req('GET', '/health'),
    login: (username: string, password: string) =>
      req<Token>('POST', '/auth/login', { body: { username, password }, form: true }),

    // Faculties
    listFaculties: () => req<Faculty[]>('GET', '/faculties'),
    getFaculty: (id: number | string) => req<Faculty>('GET', `/faculties/${id}`),
    createFaculty: (body: { name: string }) => req<Faculty>('POST', '/faculties', { body }),

    // Rooms
    listRooms: (facultyId?: number) =>
      req<Room[]>('GET', facultyId ? `/rooms/?faculty_id=${facultyId}` : '/rooms'),
    getRoom: (id: number | string) => req<Room>('GET', `/rooms/${id}`),
    createRoom: (body: { name: string; floor: number; faculty_id: number }) =>
      req<Room>('POST', '/rooms', { body }),

    // Employees
    listEmployees: (roomId?: number) =>
      req<Employee[]>('GET', roomId ? `/employees/?room_id=${roomId}` : '/employees'),
    createEmployee: (body: { jshir: string; full_name: string; room_id: number }) =>
      req<Employee>('POST', '/employees', { body }),
    updateEmployee: (id: number, body: Partial<{ jshir: string; full_name: string; room_id: number }>) =>
      req<Employee>('PATCH', `/employees/${id}`, { body }),
    deleteEmployee: (id: number) => req<void>('DELETE', `/employees/${id}`),

    // Inventory
    listInventory: () => req<Inventory[]>('GET', '/inventory'),
    createInventory: (body: {
      name: string
      employee_id: number
      image_url?: string
      ip_address?: string
      code?: string
      mac_address?: string
      device_type?: 'computer' | 'network' | 'printer'
    }) => req<Inventory>('POST', '/inventory', { body }),
    updateInventory: (id: number, body: Partial<{
      name: string
      employee_id: number
      image_url?: string
      ip_address?: string
      code?: string
      mac_address?: string
      device_type?: 'computer' | 'network' | 'printer'
    }>) => req<Inventory>('PATCH', `/inventory/${id}`, { body }),
    deleteInventory: (id: number) => req<void>('DELETE', `/inventory/${id}`),
    /** Загрузка фотографии устройства: multipart, поэтому мимо apiRequest. */
    uploadInventoryPhoto: async (id: number, file: File): Promise<ApiResult<Inventory>> => {
      const form = new FormData()
      form.append('file', file)
      try {
        const res = await fetch(`${cfg.baseUrl.replace(/\/+$/, '')}/inventory/${id}/photo`, {
          method: 'POST',
          headers: cfg.token ? { Authorization: `Bearer ${cfg.token}` } : {},
          body: form,
        })
        const data = await res.json().catch(() => null)
        return { ok: res.ok, status: res.status, data }
      } catch {
        return { ok: false, status: '—', data: null }
      }
    },

    // Mini App: вход по подписи Telegram
    miniAppAuth: (initData: string) =>
      req<{ access_token: string; user_id: number; username: string; faculty_id: number | null }>(
        'POST', '/telegram/miniapp/auth', { body: { init_data: initData } },
      ),
    miniAppLogin: (initData: string, username: string, password: string) =>
      req<{ access_token: string; user_id: number; username: string; faculty_id: number | null }>(
        'POST', '/telegram/miniapp/login',
        { body: { init_data: initData, username, password } },
      ),

    // Issues
    listIssues: () => req<Issue[]>('GET', '/issues'),
    updateIssue: (id: number, status: IssueStatus) =>
      req<Issue>('PATCH', `/issues/${id}`, { body: { status } }),

    // Workers
    listWorkers: () => req<User[]>('GET', '/users/'),
    createWorker: (body: { username: string; password: string; faculty_id?: number | null }) =>
      req<User>('POST', '/users/', { body: body as Record<string, unknown> }),
    updateWorkerFaculty: (userId: number, facultyId: number | null) =>
      req<User>('PATCH', `/users/${userId}/faculty`, {
        body: { faculty_id: facultyId } as Record<string, unknown>,
      }),
  }
}

export type Api = ReturnType<typeof createApi>
