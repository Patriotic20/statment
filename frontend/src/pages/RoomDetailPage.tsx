import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { useParams } from 'react-router-dom'
import { Plus, Users, Package, Trash2, Edit2 } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import type { Employee, Floor, Inventory, Room } from '../types'
import { errorMessage } from '../utils'
import { Breadcrumbs } from '../components/Breadcrumbs'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Field, Input, Select } from '../components/ui/Field'
import { Badge } from '../components/ui/Badge'
import { Avatar } from '../components/ui/Avatar'
import { SkeletonRows } from '../components/ui/Skeleton'
import { EmptyState } from '../components/ui/EmptyState'
import { Modal } from '../components/ui/Modal'
import { ConfirmDialog } from '../components/ui/ConfirmDialog'

const FLOOR_LABEL: Record<Floor, string> = {
  1: '1-qavat',
  2: '2-qavat',
  3: '3-qavat',
  4: '4-qavat',
}

export function RoomDetailPage() {
  const { roomId } = useParams()
  const rid = Number(roomId)
  const { api } = useAuth()
  const toast = useToast()

  const [room, setRoom] = useState<Room | null>(null)
  const [facultyName, setFacultyName] = useState('')
  const [employees, setEmployees] = useState<Employee[]>([])
  const [inventory, setInventory] = useState<Inventory[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedEmpId, setSelectedEmpId] = useState<number | null>(null)

  const [emp, setEmp] = useState({ jshir: '', full_name: '' })
  const [inv, setInv] = useState({
    name: '',
    employee_id: '',
    ip_address: '',
    code: '',
    image_url: '',
    device_type: '',
  })

  // Состояние модалок редактирования/удаления.
  const [editingEmp, setEditingEmp] = useState<Employee | null>(null)
  const [empForm, setEmpForm] = useState({ full_name: '', jshir: '' })
  const [editingInv, setEditingInv] = useState<Inventory | null>(null)
  const [invForm, setInvForm] = useState({
    name: '',
    employee_id: '',
    device_type: '',
    ip_address: '',
    code: '',
  })
  const [deletingEmp, setDeletingEmp] = useState<Employee | null>(null)
  const [deletingInv, setDeletingInv] = useState<Inventory | null>(null)
  const [busy, setBusy] = useState(false)

  const load = useCallback(async () => {
    const [roomRes, empRes, invRes] = await Promise.all([
      api.getRoom(rid),
      api.listEmployees(),
      api.listInventory(),
    ])

    if (roomRes.ok && roomRes.data) {
      setRoom(roomRes.data)
      // Вложенный faculty всегда null (бэкенд без relationship) — подгружаем имя отдельно.
      const facRes = await api.getFaculty(roomRes.data.faculty_id)
      if (facRes.ok && facRes.data) setFacultyName(facRes.data.name)
    }

    // Сотрудники этой комнаты — фильтр по колонке room_id.
    const roomEmployees =
      empRes.ok && empRes.data ? empRes.data.filter((e) => e.room_id === rid) : []
    if (empRes.ok) setEmployees(roomEmployees)
    else toast.error(errorMessage(empRes))

    // Инвентарь фильтруем по employee_id (реальная колонка), а не по вложенному employee.
    if (invRes.ok && invRes.data) {
      const ids = new Set(roomEmployees.map((e) => e.id))
      setInventory(invRes.data.filter((i) => ids.has(i.employee_id)))
    }

    setLoading(false)
  }, [api, rid, toast])

  // Поиск имени владельца по employee_id из загруженных сотрудников комнаты.
  const empById = new Map(employees.map((e) => [e.id, e]))

  useEffect(() => {
    load()
  }, [load])

  async function createEmployee(e: FormEvent) {
    e.preventDefault()
    // ЖШИР: убираем все пробелы и проверяем, что это ровно 14 цифр.
    const jshir = emp.jshir.replace(/\s+/g, '')
    if (!/^\d{14}$/.test(jshir)) {
      toast.error('JShShIR faqat 14 ta raqamdan iborat bo\'lishi kerak')
      return
    }
    const r = await api.createEmployee({
      jshir,
      full_name: emp.full_name.trim(),
      room_id: rid,
    })
    if (r.ok) {
      setEmp({ jshir: '', full_name: '' })
      toast.success('Xodim qo\'shildi')
      load()
    } else toast.error(errorMessage(r))
  }

  function openEditEmployee(e: Employee) {
    setEmpForm({ full_name: e.full_name, jshir: e.jshir })
    setEditingEmp(e)
  }

  async function saveEmployee(ev: FormEvent) {
    ev.preventDefault()
    if (!editingEmp) return
    const jshir = empForm.jshir.replace(/\s+/g, '')
    if (!/^\d{14}$/.test(jshir)) {
      toast.error('JShShIR faqat 14 ta raqamdan iborat bo\'lishi kerak')
      return
    }
    setBusy(true)
    const r = await api.updateEmployee(editingEmp.id, {
      full_name: empForm.full_name.trim(),
      jshir,
    })
    setBusy(false)
    if (r.ok) {
      setEditingEmp(null)
      toast.success('Xodim yangilandi')
      load()
    } else toast.error(errorMessage(r))
  }

  async function confirmDeleteEmployee() {
    if (!deletingEmp) return
    setBusy(true)
    const r = await api.deleteEmployee(deletingEmp.id)
    setBusy(false)
    if (r.ok) {
      if (selectedEmpId === deletingEmp.id) setSelectedEmpId(null)
      setDeletingEmp(null)
      toast.success('Xodim o\'chirildi')
      load()
    } else toast.error(errorMessage(r))
  }

  async function createInventory(e: FormEvent) {
    e.preventDefault()
    if (!inv.employee_id) {
      toast.error('Egasi bo\'lgan xodimni tanlang')
      return
    }
    const r = await api.createInventory({
      name: inv.name.trim(),
      employee_id: Number(inv.employee_id),
      ip_address: inv.ip_address.trim() || undefined,
      code: inv.code.trim() || undefined,
      image_url: inv.image_url.trim() || undefined,
      device_type:
        (inv.device_type as 'computer' | 'network' | 'printer') || undefined,
    })
    if (r.ok) {
      setInv({ name: '', employee_id: '', ip_address: '', code: '', image_url: '', device_type: '' })
      toast.success('Inventar qo\'shildi')
      load()
    } else toast.error(errorMessage(r))
  }

  function openEditInventory(i: Inventory) {
    setInvForm({
      name: i.name,
      employee_id: String(i.employee_id),
      device_type: i.device_type ?? '',
      ip_address: i.ip_address ?? '',
      code: i.code ?? '',
    })
    setEditingInv(i)
  }

  async function saveInventory(ev: FormEvent) {
    ev.preventDefault()
    if (!editingInv) return
    if (!invForm.employee_id) {
      toast.error('Egasi bo\'lgan xodimni tanlang')
      return
    }
    setBusy(true)
    const r = await api.updateInventory(editingInv.id, {
      name: invForm.name.trim(),
      employee_id: Number(invForm.employee_id),
      device_type: (invForm.device_type as 'computer' | 'network' | 'printer') || undefined,
      ip_address: invForm.ip_address.trim() || undefined,
      code: invForm.code.trim() || undefined,
    })
    setBusy(false)
    if (r.ok) {
      setEditingInv(null)
      toast.success('Inventar yangilandi')
      load()
    } else toast.error(errorMessage(r))
  }

  async function confirmDeleteInventory() {
    if (!deletingInv) return
    setBusy(true)
    const r = await api.deleteInventory(deletingInv.id)
    setBusy(false)
    if (r.ok) {
      setDeletingInv(null)
      toast.success('Inventar o\'chirildi')
      load()
    } else toast.error(errorMessage(r))
  }

  const empOptions = [
    { value: '', label: '— xodimni tanlang —' },
    ...employees.map((e) => ({ value: String(e.id), label: e.full_name })),
  ]

  const deviceTypeOptions = [
    { value: '', label: '— turini tanlang —' },
    { value: 'computer', label: '💻 Kompyuter' },
    { value: 'printer', label: '🖨 Printer' },
    { value: 'network', label: '🌐 Tarmoq' },
  ]

  return (
    <div>
      <Breadcrumbs
        items={[
          { label: 'Fakultetlar', to: '/faculties' },
          {
            label: facultyName || 'Fakultet',
            to: `/faculties/${room?.faculty_id ?? ''}`,
          },
          { label: room ? room.name : `Xona #${rid}` },
        ]}
      />
      <div className="mb-6 flex items-center gap-3">
        <h1 className="text-3xl font-semibold">{room?.name ?? `Xona #${rid}`}</h1>
        {room && <Badge tone="accent">{FLOOR_LABEL[room.floor]}</Badge>}
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* Сотрудники */}
        <section>
          <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold">
            <Users size={18} className="text-muted" /> Xodimlar
          </h2>
          <Card className="mb-4">
            <form onSubmit={createEmployee} className="space-y-3">
              <Field label="JShShIR (14 raqam)">
                <Input
                  value={emp.jshir}
                  onChange={(e) =>
                    setEmp({ ...emp, jshir: e.target.value.replace(/\D/g, '').slice(0, 14) })
                  }
                  inputMode="numeric"
                  pattern="\d{14}"
                  maxLength={14}
                  placeholder="14 raqam"
                  className="font-mono"
                  required
                />
              </Field>
              <Field label="F.I.Sh.">
                <Input
                  value={emp.full_name}
                  onChange={(e) => setEmp({ ...emp, full_name: e.target.value })}
                  required
                />
              </Field>
              <Button type="submit" icon={<Plus size={16} />}>
                Xodim qo'shish
              </Button>
            </form>
          </Card>

          {loading ? (
            <SkeletonRows />
          ) : employees.length === 0 ? (
            <EmptyState icon={Users} title="Xodimlar yo'q" hint="Yuqorida birinchisini qo'shing." />
          ) : (
            <div className="space-y-2">
              {employees.map((e) => (
                <Card 
                  key={e.id} 
                  className={`flex items-center gap-3 py-3 cursor-pointer border-2 transition ${selectedEmpId === e.id ? 'border-accent' : 'border-transparent hover:border-border'}`}
                  onClick={() => setSelectedEmpId(prev => prev === e.id ? null : e.id)}
                >
                  <Avatar name={e.full_name} />
                  <div className="min-w-0 flex-1">
                    <div className="truncate font-medium text-ink">{e.full_name}</div>
                    <div className="text-xs text-tertiary">
                      #{e.id} · <span className="font-mono">{e.jshir}</span>
                    </div>
                  </div>
                  <div className="flex gap-2 pr-2">
                    <button onClick={(ev) => { ev.stopPropagation(); openEditEmployee(e) }} className="text-muted hover:text-accent"><Edit2 size={16} /></button>
                    <button onClick={(ev) => { ev.stopPropagation(); setDeletingEmp(e) }} className="text-muted hover:text-danger"><Trash2 size={16} /></button>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </section>

        {/* Инвентарь */}
        <section>
          <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold">
            <Package size={18} className="text-muted" /> Inventar
          </h2>
          <Card className="mb-4">
            <form onSubmit={createInventory} className="space-y-3">
              <Field label="Nomi">
                <Input
                  value={inv.name}
                  onChange={(e) => setInv({ ...inv, name: e.target.value })}
                  placeholder="Masalan, Noutbuk Dell"
                  required
                />
              </Field>
              <Field label="Xodim (egasi)">
                <Select
                  value={inv.employee_id}
                  options={empOptions}
                  onChange={(e) => setInv({ ...inv, employee_id: e.target.value })}
                />
              </Field>
              <Field label="Turi">
                <Select
                  value={inv.device_type}
                  options={deviceTypeOptions}
                  onChange={(e) => setInv({ ...inv, device_type: e.target.value })}
                />
              </Field>
              <div className="grid grid-cols-2 gap-3">
                <Field label="IP-manzil (ixtiyoriy)">
                  <Input
                    value={inv.ip_address}
                    onChange={(e) => setInv({ ...inv, ip_address: e.target.value })}
                    className="font-mono"
                  />
                </Field>
                <Field label="Kod (ixtiyoriy)">
                  <Input
                    value={inv.code}
                    onChange={(e) => setInv({ ...inv, code: e.target.value })}
                    className="font-mono"
                  />
                </Field>
              </div>
              <Button
                type="submit"
                icon={<Plus size={16} />}
                disabled={employees.length === 0}
              >
                Inventar qo'shish
              </Button>
              {employees.length === 0 && (
                <p className="text-xs text-tertiary">Avval kamida bitta xodim qo'shing.</p>
              )}
            </form>
          </Card>

          {loading ? (
            <SkeletonRows />
          ) : inventory.length === 0 ? (
            <EmptyState icon={Package} title="Inventar yo'q" hint="Yuqorida uskuna qo'shing." />
          ) : (
            <div className="space-y-2">
              {inventory
                .filter(i => selectedEmpId === null || i.employee_id === selectedEmpId)
                .map((i) => (
                <Card key={i.id} className="py-3">
                  <div className="flex items-center justify-between gap-2">
                    <div className="truncate font-medium text-ink">{i.name}</div>
                    <div className="flex items-center gap-2">
                      {i.device_type && (
                        <Badge tone="neutral">
                          {deviceTypeOptions.find((o) => o.value === i.device_type)?.label ?? i.device_type}
                        </Badge>
                      )}
                      {i.code && <Badge tone="mono">{i.code}</Badge>}
                      <button onClick={() => openEditInventory(i)} className="text-muted hover:text-accent"><Edit2 size={16} /></button>
                      <button onClick={() => setDeletingInv(i)} className="text-muted hover:text-danger"><Trash2 size={16} /></button>
                    </div>
                  </div>
                  <div className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-tertiary">
                    <span>#{i.id}</span>
                    {i.ip_address && (
                      <>
                        <span>·</span>
                        <span className="font-mono">{i.ip_address}</span>
                      </>
                    )}
                    {empById.get(i.employee_id) && (
                      <>
                        <span>·</span>
                        <span>{empById.get(i.employee_id)!.full_name}</span>
                      </>
                    )}
                  </div>
                </Card>
              ))}
            </div>
          )}
        </section>
      </div>

      {/* Модалка редактирования сотрудника */}
      <Modal open={editingEmp !== null} title="Xodimni tahrirlash" onClose={() => setEditingEmp(null)}>
        <form onSubmit={saveEmployee} className="space-y-3">
          <Field label="F.I.Sh.">
            <Input
              value={empForm.full_name}
              onChange={(e) => setEmpForm({ ...empForm, full_name: e.target.value })}
              required
            />
          </Field>
          <Field label="JShShIR (14 raqam)">
            <Input
              value={empForm.jshir}
              onChange={(e) =>
                setEmpForm({ ...empForm, jshir: e.target.value.replace(/\D/g, '').slice(0, 14) })
              }
              inputMode="numeric"
              maxLength={14}
              className="font-mono"
              required
            />
          </Field>
          <div className="mt-2 flex justify-end gap-2">
            <Button type="button" variant="secondary" onClick={() => setEditingEmp(null)} disabled={busy}>
              Bekor qilish
            </Button>
            <Button type="submit" disabled={busy}>
              Saqlash
            </Button>
          </div>
        </form>
      </Modal>

      {/* Модалка редактирования инвентаря */}
      <Modal open={editingInv !== null} title="Inventarni tahrirlash" onClose={() => setEditingInv(null)}>
        <form onSubmit={saveInventory} className="space-y-3">
          <Field label="Nomi">
            <Input
              value={invForm.name}
              onChange={(e) => setInvForm({ ...invForm, name: e.target.value })}
              required
            />
          </Field>
          <Field label="Xodim (egasi)">
            <Select
              value={invForm.employee_id}
              options={empOptions}
              onChange={(e) => setInvForm({ ...invForm, employee_id: e.target.value })}
            />
          </Field>
          <Field label="Turi">
            <Select
              value={invForm.device_type}
              options={deviceTypeOptions}
              onChange={(e) => setInvForm({ ...invForm, device_type: e.target.value })}
            />
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="IP-manzil (ixtiyoriy)">
              <Input
                value={invForm.ip_address}
                onChange={(e) => setInvForm({ ...invForm, ip_address: e.target.value })}
                className="font-mono"
              />
            </Field>
            <Field label="Kod (ixtiyoriy)">
              <Input
                value={invForm.code}
                onChange={(e) => setInvForm({ ...invForm, code: e.target.value })}
                className="font-mono"
              />
            </Field>
          </div>
          <div className="mt-2 flex justify-end gap-2">
            <Button type="button" variant="secondary" onClick={() => setEditingInv(null)} disabled={busy}>
              Bekor qilish
            </Button>
            <Button type="submit" disabled={busy}>
              Saqlash
            </Button>
          </div>
        </form>
      </Modal>

      <ConfirmDialog
        open={deletingEmp !== null}
        title="Xodimni o'chirish"
        message={`«${deletingEmp?.full_name ?? ''}» xodimini o'chirishga ishonchingiz komilmi?`}
        loading={busy}
        onConfirm={confirmDeleteEmployee}
        onClose={() => setDeletingEmp(null)}
      />

      <ConfirmDialog
        open={deletingInv !== null}
        title="Inventarni o'chirish"
        message={`«${deletingInv?.name ?? ''}» uskunasini o'chirishga ishonchingiz komilmi?`}
        loading={busy}
        onConfirm={confirmDeleteInventory}
        onClose={() => setDeletingInv(null)}
      />
    </div>
  )
}
