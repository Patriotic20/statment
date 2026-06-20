import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { Users, Plus, Trash2 } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import type { User, Faculty } from '../types'
import { errorMessage } from '../utils'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { Field, Input, Select } from '../components/ui/Field'
import { EmptyState } from '../components/ui/EmptyState'

export function WorkersPage() {
  const { api } = useAuth()
  const { success, error } = useToast()
  const [workers, setWorkers] = useState<User[]>([])
  const [faculties, setFaculties] = useState<Faculty[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState<Record<number, boolean>>({})

  const [selectedFaculties, setSelectedFaculties] = useState<Record<number, string>>({})
  const [newWorker, setNewWorker] = useState({ username: '', password: '', faculty_id: '' })
  const [creating, setCreating] = useState(false)

  const load = useCallback(async () => {
    const [workersRes, facultiesRes] = await Promise.all([
      api.listWorkers(),
      api.listFaculties(),
    ])
    if (workersRes.ok && workersRes.data) setWorkers(workersRes.data)
    if (facultiesRes.ok && facultiesRes.data) setFaculties(facultiesRes.data)
    setLoading(false)
  }, [api])

  useEffect(() => {
    load()
  }, [load])

  const handleFacultyChange = async (userId: number, value: string) => {
    const facultyId = value === '' ? null : Number(value)
    setSaving((prev) => ({ ...prev, [userId]: true }))
    try {
      const res = await api.updateWorkerFaculty(userId, facultyId)
      if (res.ok && res.data) {
        setWorkers((prev) => prev.map((w) => (w.id === userId ? res.data! : w)))
        success('Fakultet yangilandi')
        setSelectedFaculties((prev) => ({ ...prev, [userId]: '' }))
      } else {
        error('Fakultetni yangilab bo\'lmadi')
      }
    } catch {
      error('Yangilashda xato')
    } finally {
      setSaving((prev) => ({ ...prev, [userId]: false }))
    }
  }

  async function handleCreateWorker(e: FormEvent) {
    e.preventDefault()
    const username = newWorker.username.trim()
    if (!username || !newWorker.password) {
      error('Login va parolni kiriting')
      return
    }
    setCreating(true)
    const r = await api.createWorker({
      username,
      password: newWorker.password,
      faculty_id: newWorker.faculty_id ? Number(newWorker.faculty_id) : undefined,
    })
    setCreating(false)
    if (r.ok) {
      setNewWorker({ username: '', password: '', faculty_id: '' })
      success('Ishchi qo\'shildi')
      load()
    } else {
      error(errorMessage(r))
    }
  }

  if (loading) return <div className="text-muted">Yuklanmoqda...</div>

  const unassignedWorkers = workers.filter((w) => !w.faculty_id)
  const facultyOptions = [
    { value: '', label: '— Fakultetni tanlang —' },
    ...faculties.map((f) => ({ value: String(f.id), label: f.name })),
  ]

  return (
    <div>
      <h1 className="mb-6 text-3xl font-semibold">Ishchilar</h1>

      <Card className="mb-8">
        <form onSubmit={handleCreateWorker} className="flex flex-wrap items-end gap-3">
          <div className="min-w-[160px] flex-1">
            <Field label="Login">
              <Input
                value={newWorker.username}
                onChange={(e) => setNewWorker({ ...newWorker, username: e.target.value })}
                placeholder="Masalan, worker_fit"
                required
              />
            </Field>
          </div>
          <div className="min-w-[160px] flex-1">
            <Field label="Parol">
              <Input
                type="password"
                value={newWorker.password}
                onChange={(e) => setNewWorker({ ...newWorker, password: e.target.value })}
                required
              />
            </Field>
          </div>
          <div className="min-w-[180px] flex-1">
            <Field label="Fakultet (ixtiyoriy)">
              <Select
                value={newWorker.faculty_id}
                options={facultyOptions}
                onChange={(e) => setNewWorker({ ...newWorker, faculty_id: e.target.value })}
              />
            </Field>
          </div>
          <Button type="submit" icon={<Plus size={16} />} disabled={creating}>
            Ishchi qo'shish
          </Button>
        </form>
      </Card>

      {unassignedWorkers.length > 0 && (
        <Card className="mb-8">
          <div className="mb-4 flex items-center gap-2">
            <Badge tone="danger">Biriktirilmagan</Badge>
            <span className="text-sm text-muted">{unassignedWorkers.length} ta ishchi</span>
          </div>
          <div className="space-y-3">
            {unassignedWorkers.map((worker) => (
              <div
                key={worker.id}
                className="flex flex-wrap items-center gap-3 rounded-input bg-canvas-soft p-3"
              >
                <div className="min-w-[140px] flex-1">
                  <div className="font-medium text-ink">{worker.username}</div>
                  <div className="text-xs text-muted">
                    Telegram ID: {worker.telegram_id || 'biriktirilmagan'}
                  </div>
                </div>
                <Select
                  className="sm:w-auto sm:min-w-[200px]"
                  value={selectedFaculties[worker.id] ?? ''}
                  disabled={saving[worker.id]}
                  onChange={(e) =>
                    setSelectedFaculties((prev) => ({ ...prev, [worker.id]: e.target.value }))
                  }
                  options={facultyOptions}
                />
                <Button
                  size="sm"
                  disabled={!selectedFaculties[worker.id] || saving[worker.id]}
                  onClick={() => handleFacultyChange(worker.id, selectedFaculties[worker.id])}
                >
                  Biriktirish
                </Button>
              </div>
            ))}
          </div>
        </Card>
      )}

      {faculties.length === 0 ? (
        <EmptyState icon={Users} title="Hozircha fakultetlar yo'q" />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {faculties.map((faculty) => {
            const fWorkers = workers.filter((w) => w.faculty_id === faculty.id)
            return (
              <Card key={faculty.id} className="flex flex-col">
                <h3 className="mb-3 border-b border-border pb-2 font-semibold text-ink">
                  {faculty.name}
                </h3>
                {fWorkers.length === 0 ? (
                  <p className="flex-1 text-sm text-muted">Ishchilar yo'q</p>
                ) : (
                  <div className="flex-1 space-y-1">
                    {fWorkers.map((w) => (
                      <div
                        key={w.id}
                        className="flex items-center justify-between rounded-md px-2 py-1.5 hover:bg-canvas-soft"
                      >
                        <span className="text-sm font-medium text-ink">{w.username}</span>
                        <button
                          disabled={saving[w.id]}
                          onClick={() => handleFacultyChange(w.id, '')}
                          className="text-muted transition hover:text-danger disabled:opacity-50"
                          aria-label="Fakultetdan olib tashlash"
                          title="Fakultetdan olib tashlash"
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
