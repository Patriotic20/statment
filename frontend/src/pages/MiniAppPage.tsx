import { useCallback, useEffect, useMemo, useState, type FormEvent } from 'react'
import { Building2, LogIn, Package, UserPlus } from 'lucide-react'
import { createApi } from '../api/endpoints'
import { Button } from '../components/ui/Button'
import { Field, Input, PasswordInput, Select } from '../components/ui/Field'
import type { Employee, Faculty, Room } from '../types'
import { errorMessage } from '../utils'

/** Telegram отдаёт SDK через глобальный объект; типизируем только нужное. */
interface TelegramWebApp {
  initData: string
  ready: () => void
  expand: () => void
  colorScheme?: string
  themeParams?: Record<string, string>
  HapticFeedback?: { notificationOccurred: (type: 'success' | 'error' | 'warning') => void }
}

function telegram(): TelegramWebApp | null {
  return (window as unknown as { Telegram?: { WebApp?: TelegramWebApp } }).Telegram?.WebApp ?? null
}

type Screen = 'menu' | 'room' | 'employee' | 'inventory'

const DEVICE_OPTIONS = [
  { value: '', label: '— qurilma turi —' },
  { value: 'computer', label: '💻 Kompyuter' },
  { value: 'printer', label: '🖨 Printer' },
  { value: 'network', label: '🌐 Tarmoq qurilmasi' },
]

const FLOOR_OPTIONS = [1, 2, 3, 4].map((n) => ({ value: String(n), label: `${n}-qavat` }))

export function MiniAppPage() {
  const [token, setToken] = useState<string | null>(null)
  const [username, setUsername] = useState('')
  const [status, setStatus] = useState<'checking' | 'login' | 'ready'>('checking')
  const [screen, setScreen] = useState<Screen>('menu')
  const [note, setNote] = useState<{ text: string; ok: boolean } | null>(null)
  const [busy, setBusy] = useState(false)

  const [faculties, setFaculties] = useState<Faculty[]>([])
  const [rooms, setRooms] = useState<Room[]>([])
  const [employees, setEmployees] = useState<Employee[]>([])

  const api = useMemo(() => createApi({ baseUrl: '/api', token: token ?? undefined }), [token])
  const initData = telegram()?.initData ?? ''

  // ── Вход ───────────────────────────────────────────────────────────────
  const [creds, setCreds] = useState({ username: '', password: '' })

  useEffect(() => {
    const tg = telegram()
    tg?.ready()
    tg?.expand()
  }, [])

  useEffect(() => {
    let cancelled = false
    async function auth() {
      if (!initData) {
        // Страницу открыли не из Telegram — подписи нет, показываем вход.
        if (!cancelled) setStatus('login')
        return
      }
      const r = await createApi({ baseUrl: '/api' }).miniAppAuth(initData)
      if (cancelled) return
      if (r.ok && r.data) {
        setToken(r.data.access_token)
        setUsername(r.data.username)
        setStatus('ready')
      } else {
        setStatus('login')
      }
    }
    auth()
    return () => { cancelled = true }
  }, [initData])

  async function handleLogin(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    const anon = createApi({ baseUrl: '/api' })
    const name = creds.username.trim()
    // Из Telegram — вход с привязкой аккаунта (дальше пускает молча).
    // Вне Telegram подписи нет, поэтому обычный вход по паролю, как в панели.
    const r = initData
      ? await anon.miniAppLogin(initData, name, creds.password)
      : await anon.login(name, creds.password)
    setBusy(false)
    if (r.ok && r.data) {
      setToken(r.data.access_token)
      setUsername(name)
      setStatus('ready')
      setNote(null)
    } else {
      setNote({ text: errorMessage(r), ok: false })
    }
  }

  // ── Справочники ────────────────────────────────────────────────────────
  const loadFaculties = useCallback(async () => {
    const r = await api.listFaculties()
    if (r.ok && r.data) setFaculties(r.data)
  }, [api])

  useEffect(() => {
    if (status === 'ready') loadFaculties()
  }, [status, loadFaculties])

  async function loadRooms(facultyId: string) {
    if (!facultyId) { setRooms([]); return }
    const r = await api.listRooms(Number(facultyId))
    setRooms(r.ok && r.data ? r.data : [])
  }

  async function loadEmployees(roomId: string) {
    if (!roomId) { setEmployees([]); return }
    const r = await api.listEmployees(Number(roomId))
    setEmployees(r.ok && r.data ? r.data : [])
  }

  function finish(text: string, ok: boolean) {
    setNote({ text, ok })
    telegram()?.HapticFeedback?.notificationOccurred(ok ? 'success' : 'error')
    if (ok) setScreen('menu')
  }

  // ── Формы ──────────────────────────────────────────────────────────────
  const [roomForm, setRoomForm] = useState({ name: '', floor: '1', faculty_id: '' })
  const [empForm, setEmpForm] = useState({ jshir: '', full_name: '', faculty_id: '', room_id: '' })
  const [invForm, setInvForm] = useState({
    name: '', device_type: '', ip_address: '', mac_address: '',
    faculty_id: '', room_id: '', employee_id: '',
  })
  const [photo, setPhoto] = useState<File | null>(null)

  async function submitRoom(e: FormEvent) {
    e.preventDefault()
    if (!roomForm.faculty_id) return finish('Fakultetni tanlang', false)
    setBusy(true)
    const r = await api.createRoom({
      name: roomForm.name.trim(),
      floor: Number(roomForm.floor),
      faculty_id: Number(roomForm.faculty_id),
    })
    setBusy(false)
    if (r.ok) {
      setRoomForm({ name: '', floor: '1', faculty_id: '' })
      finish('✅ Xona qo\'shildi', true)
    } else finish(errorMessage(r), false)
  }

  async function submitEmployee(e: FormEvent) {
    e.preventDefault()
    if (!empForm.room_id) return finish('Xonani tanlang', false)
    setBusy(true)
    const r = await api.createEmployee({
      jshir: empForm.jshir.trim(),
      full_name: empForm.full_name.trim(),
      room_id: Number(empForm.room_id),
    })
    setBusy(false)
    if (r.ok) {
      setEmpForm({ jshir: '', full_name: '', faculty_id: '', room_id: '' })
      finish('✅ Xodim qo\'shildi', true)
    } else finish(errorMessage(r), false)
  }

  async function submitInventory(e: FormEvent) {
    e.preventDefault()
    if (!invForm.employee_id) return finish('Xodimni tanlang', false)
    setBusy(true)
    const r = await api.createInventory({
      name: invForm.name.trim(),
      employee_id: Number(invForm.employee_id),
      device_type: (invForm.device_type as 'computer' | 'network' | 'printer') || undefined,
      ip_address: invForm.ip_address.trim() || undefined,
      mac_address: invForm.mac_address.trim() || undefined,
    })
    if (!r.ok || !r.data) {
      setBusy(false)
      return finish(errorMessage(r), false)
    }
    // Запись создана; фото — отдельным запросом, его сбой не отменяет карточку.
    let photoNote = ''
    if (photo) {
      const up = await api.uploadInventoryPhoto(r.data.id, photo)
      photoNote = up.ok ? ', rasm yuklandi' : ', ⚠️ rasm yuklanmadi'
    }
    setBusy(false)
    setInvForm({ name: '', device_type: '', ip_address: '', mac_address: '', faculty_id: '', room_id: '', employee_id: '' })
    setPhoto(null)
    finish(`✅ Uskuna qo'shildi${photoNote}`, true)
  }

  // ── Экраны ─────────────────────────────────────────────────────────────
  if (status === 'checking') {
    return <Centered>Yuklanmoqda…</Centered>
  }

  if (status === 'login') {
    return (
      <div className="mx-auto max-w-md px-4 py-8">
        <h1 className="font-serif text-2xl text-ink">RRTM</h1>
        <p className="mt-1 text-sm text-muted">
          {initData ? 'Hisobingizni bir marta bog\'lang' : 'Login va parol bilan kiring'}
        </p>
        <form onSubmit={handleLogin} className="mt-6 space-y-4">
          <Field label="Foydalanuvchi nomi">
            <Input value={creds.username} autoCapitalize="none"
              onChange={(e) => setCreds({ ...creds, username: e.target.value })} />
          </Field>
          <Field label="Parol">
            <PasswordInput value={creds.password} autoComplete="current-password"
              onChange={(e) => setCreds({ ...creds, password: e.target.value })} />
          </Field>
          <Button type="submit" icon={<LogIn size={16} />} disabled={busy} className="w-full justify-center">
            Kirish
          </Button>
        </form>
        {note && <Note note={note} />}
      </div>
    )
  }

  const facultyOptions = [{ value: '', label: '— fakultet —' },
    ...faculties.map((f) => ({ value: String(f.id), label: f.name }))]
  const roomOptions = [{ value: '', label: '— xona —' },
    ...rooms.map((r) => ({ value: String(r.id), label: r.name }))]
  const employeeOptions = [{ value: '', label: '— xodim —' },
    ...employees.map((e) => ({ value: String(e.id), label: e.full_name }))]

  return (
    <div className="mx-auto max-w-md px-4 py-5 pb-16">
      <header className="mb-5 flex items-center justify-between">
        <div>
          <div className="font-serif text-xl text-ink">RRTM</div>
          <div className="text-xs text-tertiary">{username}</div>
        </div>
        {screen !== 'menu' && (
          <Button variant="secondary" size="sm" onClick={() => { setScreen('menu'); setNote(null) }}>
            ← Orqaga
          </Button>
        )}
      </header>

      {note && <Note note={note} />}

      {screen === 'menu' && (
        <div className="space-y-3">
          <MenuCard icon={<Building2 size={20} />} title="Xona qo'shish"
            hint="Nomi, qavati va fakulteti" onClick={() => setScreen('room')} />
          <MenuCard icon={<UserPlus size={20} />} title="Xodim qo'shish"
            hint="JShShIR, F.I.Sh. va xonasi" onClick={() => setScreen('employee')} />
          <MenuCard icon={<Package size={20} />} title="Uskuna qo'shish"
            hint="Rasm, IP va MAC bilan" onClick={() => setScreen('inventory')} />
        </div>
      )}

      {screen === 'room' && (
        <form onSubmit={submitRoom} className="space-y-4">
          <Field label="Xona nomi">
            <Input value={roomForm.name} placeholder="305-xona" required
              onChange={(e) => setRoomForm({ ...roomForm, name: e.target.value })} />
          </Field>
          <Field label="Qavat">
            <Select value={roomForm.floor} options={FLOOR_OPTIONS}
              onChange={(e) => setRoomForm({ ...roomForm, floor: e.target.value })} />
          </Field>
          <Field label="Fakultet">
            <Select value={roomForm.faculty_id} options={facultyOptions}
              onChange={(e) => setRoomForm({ ...roomForm, faculty_id: e.target.value })} />
          </Field>
          <Button type="submit" disabled={busy} className="w-full justify-center">Saqlash</Button>
        </form>
      )}

      {screen === 'employee' && (
        <form onSubmit={submitEmployee} className="space-y-4">
          <Field label="JShShIR (14 ta raqam)">
            <Input value={empForm.jshir} inputMode="numeric" maxLength={14} required className="font-mono"
              onChange={(e) => setEmpForm({ ...empForm, jshir: e.target.value })} />
          </Field>
          <Field label="F.I.Sh.">
            <Input value={empForm.full_name} required
              onChange={(e) => setEmpForm({ ...empForm, full_name: e.target.value })} />
          </Field>
          <Field label="Fakultet">
            <Select value={empForm.faculty_id} options={facultyOptions}
              onChange={(e) => {
                setEmpForm({ ...empForm, faculty_id: e.target.value, room_id: '' })
                loadRooms(e.target.value)
              }} />
          </Field>
          <Field label="Xona">
            <Select value={empForm.room_id} options={roomOptions}
              onChange={(e) => setEmpForm({ ...empForm, room_id: e.target.value })} />
          </Field>
          <Button type="submit" disabled={busy} className="w-full justify-center">Saqlash</Button>
        </form>
      )}

      {screen === 'inventory' && (
        <form onSubmit={submitInventory} className="space-y-4">
          <Field label="Uskuna nomi">
            <Input value={invForm.name} placeholder="Dell Optiplex 7090" required
              onChange={(e) => setInvForm({ ...invForm, name: e.target.value })} />
          </Field>
          <Field label="Turi">
            <Select value={invForm.device_type} options={DEVICE_OPTIONS}
              onChange={(e) => setInvForm({ ...invForm, device_type: e.target.value })} />
          </Field>
          <Field label="Rasm (ixtiyoriy)">
            <input type="file" accept="image/*" capture="environment"
              onChange={(e) => setPhoto(e.target.files?.[0] ?? null)}
              className="w-full rounded-input border border-border bg-surface px-3 py-2 text-sm text-muted" />
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="IP (ixtiyoriy)">
              <Input value={invForm.ip_address} inputMode="decimal" className="font-mono"
                onChange={(e) => setInvForm({ ...invForm, ip_address: e.target.value })} />
            </Field>
            <Field label="MAC (ixtiyoriy)">
              <Input value={invForm.mac_address} className="font-mono" placeholder="AA:BB:CC:DD:EE:FF"
                onChange={(e) => setInvForm({ ...invForm, mac_address: e.target.value })} />
            </Field>
          </div>
          <Field label="Fakultet">
            <Select value={invForm.faculty_id} options={facultyOptions}
              onChange={(e) => {
                setInvForm({ ...invForm, faculty_id: e.target.value, room_id: '', employee_id: '' })
                setEmployees([])
                loadRooms(e.target.value)
              }} />
          </Field>
          <Field label="Xona">
            <Select value={invForm.room_id} options={roomOptions}
              onChange={(e) => {
                setInvForm({ ...invForm, room_id: e.target.value, employee_id: '' })
                loadEmployees(e.target.value)
              }} />
          </Field>
          <Field label="Egasi (xodim)">
            <Select value={invForm.employee_id} options={employeeOptions}
              onChange={(e) => setInvForm({ ...invForm, employee_id: e.target.value })} />
          </Field>
          <Button type="submit" disabled={busy} className="w-full justify-center">Saqlash</Button>
        </form>
      )}
    </div>
  )
}

function Centered({ children }: { children: React.ReactNode }) {
  return <div className="grid min-h-screen place-items-center text-sm text-muted">{children}</div>
}

function Note({ note }: { note: { text: string; ok: boolean } }) {
  return (
    <div className={`mb-4 rounded-card border px-3 py-2 text-sm ${
      note.ok ? 'border-border bg-surface text-ink' : 'border-danger/30 bg-danger/5 text-danger'
    }`}>
      {note.text}
    </div>
  )
}

function MenuCard({ icon, title, hint, onClick }: {
  icon: React.ReactNode; title: string; hint: string; onClick: () => void
}) {
  return (
    <button type="button" onClick={onClick}
      className="flex w-full items-center gap-3 rounded-card border border-border bg-surface px-4 py-4 text-left shadow-sm transition active:bg-canvas-soft">
      <span className="grid h-10 w-10 shrink-0 place-items-center rounded-input bg-accent-soft text-accent">
        {icon}
      </span>
      <span className="min-w-0">
        <span className="block font-medium text-ink">{title}</span>
        <span className="block text-xs text-tertiary">{hint}</span>
      </span>
    </button>
  )
}
