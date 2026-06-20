import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { DoorOpen, Plus } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import type { Faculty, Floor, Room } from '../types'
import { errorMessage } from '../utils'
import { Breadcrumbs } from '../components/Breadcrumbs'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Field, Input, Select } from '../components/ui/Field'
import { Badge } from '../components/ui/Badge'
import { SkeletonCards } from '../components/ui/Skeleton'
import { EmptyState } from '../components/ui/EmptyState'

const FLOORS: { value: string; label: string }[] = [
  { value: '1', label: '1-qavat' },
  { value: '2', label: '2-qavat' },
  { value: '3', label: '3-qavat' },
  { value: '4', label: '4-qavat' },
]

const FLOOR_LABEL: Record<Floor, string> = {
  1: '1-qavat',
  2: '2-qavat',
  3: '3-qavat',
  4: '4-qavat',
}

export function FacultyDetailPage() {
  const { facultyId } = useParams()
  const fid = Number(facultyId)
  const { api } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()

  const [faculty, setFaculty] = useState<Faculty | null>(null)
  const [rooms, setRooms] = useState<Room[]>([])
  const [name, setName] = useState('')
  const [floor, setFloor] = useState<Floor>(1)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    const [fRes, rRes] = await Promise.all([api.getFaculty(fid), api.listRooms()])
    if (fRes.ok && fRes.data) setFaculty(fRes.data)
    if (rRes.ok && rRes.data) setRooms(rRes.data.filter((r) => r.faculty_id === fid))
    else if (!rRes.ok) toast.error(errorMessage(rRes))
    setLoading(false)
  }, [api, fid, toast])

  useEffect(() => {
    load()
  }, [load])

  async function create(e: FormEvent) {
    e.preventDefault()
    const r = await api.createRoom({ name: name.trim(), floor, faculty_id: fid })
    if (r.ok) {
      setName('')
      setFloor(1)
      toast.success('Xona yaratildi')
      load()
    } else toast.error(errorMessage(r))
  }

  return (
    <div>
      <Breadcrumbs
        items={[
          { label: 'Fakultetlar', to: '/faculties' },
          { label: faculty?.name ?? `Fakultet #${fid}` },
        ]}
      />
      <h1 className="mb-1 text-3xl font-semibold">{faculty?.name ?? 'Fakultet'}</h1>
      <p className="mb-6 text-sm text-muted">Fakultet xonalari. Inventar va xodimlar uchun xonani oching.</p>

      <Card className="mb-6">
        <form onSubmit={create} className="flex flex-wrap items-end gap-3">
          <div className="min-w-[160px] flex-1">
            <Field label="Xona nomi">
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Masalan, 204"
                required
              />
            </Field>
          </div>
          <div className="min-w-[140px]">
            <Field label="Qavat">
              <Select
                value={String(floor)}
                options={FLOORS}
                onChange={(e) => setFloor(Number(e.target.value) as Floor)}
              />
            </Field>
          </div>
          <Button type="submit" icon={<Plus size={16} />}>
            Yaratish
          </Button>
        </form>
      </Card>

      {loading ? (
        <SkeletonCards />
      ) : rooms.length === 0 ? (
        <EmptyState
          icon={DoorOpen}
          title="Ushbu fakultetda xonalar yo'q"
          hint="Yuqoridagi shaklda xona qo'shing va qavatni tanlang."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {rooms.map((room) => (
            <Card key={room.id} onClick={() => navigate(`/rooms/${room.id}`)}>
              <div className="flex items-start justify-between">
                <span className="grid h-10 w-10 place-items-center rounded-input bg-accent-soft text-accent">
                  <DoorOpen size={18} />
                </span>
                <Badge tone="neutral">{FLOOR_LABEL[room.floor]}</Badge>
              </div>
              <div className="mt-3 text-lg font-medium text-ink">{room.name}</div>
              <div className="mt-1 text-xs text-tertiary">Xona #{room.id}</div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
