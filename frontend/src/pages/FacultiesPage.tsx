import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { Building2, Plus, DoorOpen } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import type { Faculty } from '../types'
import { errorMessage } from '../utils'
import { Breadcrumbs } from '../components/Breadcrumbs'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Field, Input } from '../components/ui/Field'
import { Badge } from '../components/ui/Badge'
import { SkeletonCards } from '../components/ui/Skeleton'
import { EmptyState } from '../components/ui/EmptyState'

export function FacultiesPage() {
  const { api } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()
  const [items, setItems] = useState<Faculty[]>([])
  const [roomCounts, setRoomCounts] = useState<Record<number, number>>({})
  const [name, setName] = useState('')
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    const [fRes, rRes] = await Promise.all([api.listFaculties(), api.listRooms()])
    if (fRes.ok && fRes.data) setItems(fRes.data)
    else toast.error(errorMessage(fRes))
    if (rRes.ok && rRes.data) {
      const counts: Record<number, number> = {}
      for (const r of rRes.data) counts[r.faculty_id] = (counts[r.faculty_id] ?? 0) + 1
      setRoomCounts(counts)
    }
    setLoading(false)
  }, [api, toast])

  useEffect(() => {
    load()
  }, [load])

  async function create(e: FormEvent) {
    e.preventDefault()
    const r = await api.createFaculty({ name: name.trim() })
    if (r.ok) {
      setName('')
      toast.success('Fakultet yaratildi')
      load()
    } else toast.error(errorMessage(r))
  }

  return (
    <div>
      <Breadcrumbs items={[{ label: 'Fakultetlar' }]} />
      <h1 className="mb-6 text-3xl font-semibold">Fakultetlar</h1>

      <Card className="mb-6">
        <form onSubmit={create} className="flex flex-wrap items-end gap-3">
          <div className="min-w-[200px] flex-1">
            <Field label="Fakultet nomi">
              <Input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Masalan, Informatika"
                required
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
      ) : items.length === 0 ? (
        <EmptyState
          icon={Building2}
          title="Hozircha fakultetlar yo'q"
          hint="Yuqoridagi shakl yordamida birinchi fakultetni yarating."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((f) => (
            <Card key={f.id} onClick={() => navigate(`/faculties/${f.id}`)}>
              <div className="flex items-start justify-between">
                <span className="grid h-10 w-10 place-items-center rounded-input bg-accent-soft text-accent">
                  <Building2 size={18} />
                </span>
                <Badge tone="neutral">
                  <DoorOpen size={12} className="mr-1" />
                  {roomCounts[f.id] ?? 0} xona.
                </Badge>
              </div>
              <div className="mt-3 text-lg font-medium text-ink">{f.name}</div>
              <div className="mt-1 text-xs text-tertiary">Fakultet #{f.id}</div>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
