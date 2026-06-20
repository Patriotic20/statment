/** Этаж: бэкенд использует целочисленный enum (1=FIRST … 4=FOURTH). */
export type Floor = 1 | 2 | 3 | 4

export interface Token {
  access_token: string
  token_type: string
}

export interface Faculty {
  id: number
  name: string
  created_at: string
  updated_at: string
}

export interface Room {
  id: number
  name: string
  floor: Floor
  faculty_id: number
  faculty?: Faculty
  created_at: string
  updated_at: string
}

export interface Employee {
  id: number
  jshir: string
  full_name: string
  room_id: number
  room?: Room
  created_at: string
  updated_at: string
}

export interface Inventory {
  id: number
  name: string
  image_url: string | null
  ip_address: string | null
  code: string | null
  device_type: 'computer' | 'network' | 'printer' | null
  employee_id: number
  employee?: Employee
  created_at: string
  updated_at: string
}

/** Запись в логе запросов/ответов. */
export interface LogItem {
  id: number
  method: string
  path: string
  status: number | string
  text: string
  ok: boolean
}

export type IssueType = 'computer' | 'network' | 'printer'
export type IssueStatus = 'new' | 'in_progress' | 'resolved'

export interface Issue {
  id: number
  issue_type: IssueType
  status: IssueStatus
  employee_id: number
  telegram_id: number
  created_at: string
  updated_at: string
}

export interface User {
  id: number
  username: string
  telegram_id: number | null
  faculty_id: number | null
  created_at: string
  updated_at: string
}
