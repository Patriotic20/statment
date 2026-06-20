import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { useIssuesWebSocket } from '../hooks/useIssuesWebSocket'
import { Issue, IssueStatus, Employee, Room, Inventory } from '../types'
import { Laptop, Network, Printer, X, MonitorSmartphone } from 'lucide-react'

export function IssuesPage() {
  const { api, token } = useAuth()
  const { success } = useToast()
  const [issues, setIssues] = useState<Issue[]>([])
  const [employees, setEmployees] = useState<Record<number, Employee>>({})
  const [rooms, setRooms] = useState<Record<number, Room>>({})
  const [inventory, setInventory] = useState<Inventory[]>([])
  const [loading, setLoading] = useState(true)
  
  const [selectedIssue, setSelectedIssue] = useState<Issue | null>(null)

  useEffect(() => {
    async function load() {
      try {
        const [issuesRes, employeesRes, roomsRes, invRes] = await Promise.all([
          api.listIssues(),
          api.listEmployees(),
          api.listRooms(),
          api.listInventory()
        ])
        
        if (issuesRes.ok && issuesRes.data) setIssues(issuesRes.data)
        
        if (employeesRes.ok && employeesRes.data) {
          const empMap: Record<number, Employee> = {}
          employeesRes.data.forEach(emp => { empMap[emp.id] = emp })
          setEmployees(empMap)
        }

        if (roomsRes.ok && roomsRes.data) {
          const rMap: Record<number, Room> = {}
          roomsRes.data.forEach(r => { rMap[r.id] = r })
          setRooms(rMap)
        }
        
        if (invRes.ok && invRes.data) {
          setInventory(invRes.data)
        }
      } catch (err) {
        console.error('Failed to fetch data:', err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [api])

  useIssuesWebSocket(
    token,
    (issue) => {
      setIssues((prev) => [issue, ...prev])
      success(`Yangi ariza #${issue.id}`)
    },
    (issue) => {
      setIssues((prev) => prev.map((i) => (i.id === issue.id ? issue : i)))
      setSelectedIssue((prev) => (prev?.id === issue.id ? issue : prev))
    },
  )

  const handleStatusChange = async (id: number, newStatus: IssueStatus) => {
    try {
      const res = await api.updateIssue(id, newStatus)
      if (res.ok && res.data) {
        setIssues(issues.map(issue => issue.id === id ? res.data! : issue))
        if (selectedIssue && selectedIssue.id === id) {
          setSelectedIssue(res.data!)
        }
      }
    } catch (err) {
      console.error('Failed to update issue:', err)
    }
  }

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'computer': return <span className="flex items-center gap-1.5"><Laptop size={15} /> Kompyuter</span>
      case 'network': return <span className="flex items-center gap-1.5"><Network size={15} /> Tarmoq</span>
      case 'printer': return <span className="flex items-center gap-1.5"><Printer size={15} /> Printer</span>
      default: return type
    }
  }

  const getStatusLabel = (status: IssueStatus) => {
    switch (status) {
      case 'new': return <span className="inline-flex items-center rounded-full bg-danger/10 px-2 py-0.5 text-xs font-semibold text-danger">Yangi</span>
      case 'in_progress': return <span className="inline-flex items-center rounded-full bg-warning/10 px-2 py-0.5 text-xs font-semibold text-warning-dark">Jarayonda</span>
      case 'resolved': return <span className="inline-flex items-center rounded-full bg-success/10 px-2 py-0.5 text-xs font-semibold text-success-dark">Hal qilindi</span>
      default: return status
    }
  }

  if (loading) return <div className="text-muted">Yuklanmoqda...</div>

  const sortedIssues = [...issues].sort((a, b) => {
    const statusOrder = { new: 0, in_progress: 1, resolved: 2 }
    if (statusOrder[a.status] !== statusOrder[b.status]) {
      return statusOrder[a.status] - statusOrder[b.status]
    }
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Arizalar</h1>
        <p className="text-sm text-muted">Barcha murojaatlar va ta'mirlash uchun arizalar ro'yxati</p>
      </div>

      <div className="overflow-hidden rounded-lg border border-border bg-surface shadow-sm">
        <table className="w-full text-left text-sm">
          <thead className="bg-canvas-soft text-muted border-b border-border uppercase tracking-wider text-xs">
            <tr>
              <th className="px-5 py-4 font-semibold">ID</th>
              <th className="px-5 py-4 font-semibold">Turi</th>
              <th className="px-5 py-4 font-semibold">Holati</th>
              <th className="px-5 py-4 font-semibold">Xodim</th>
              <th className="px-5 py-4 font-semibold">Xona</th>
              <th className="px-5 py-4 font-semibold">Yaratilgan sana</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {sortedIssues.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-5 py-8 text-center text-muted">Arizalar yo'q</td>
              </tr>
            ) : (
              sortedIssues.map(issue => {
                const emp = employees[issue.employee_id]
                const roomName = emp ? rooms[emp.room_id]?.name || '-' : '-'
                return (
                  <tr 
                    key={issue.id} 
                    onClick={() => setSelectedIssue(issue)}
                    className="cursor-pointer transition hover:bg-canvas hover:shadow-inner"
                  >
                    <td className="px-5 py-4 font-medium text-muted">#{issue.id}</td>
                    <td className="px-5 py-4 font-medium">{getTypeLabel(issue.issue_type)}</td>
                    <td className="px-5 py-4">{getStatusLabel(issue.status)}</td>
                    <td className="px-5 py-4 truncate max-w-[200px]" title={emp?.full_name}>{emp?.full_name || `ID ${issue.employee_id}`}</td>
                    <td className="px-5 py-4">{roomName}</td>
                    <td className="px-5 py-4 text-muted whitespace-nowrap">{new Date(issue.created_at).toLocaleString()}</td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Modal / Slide-over for Details */}
      {selectedIssue && (
        <div className="fixed inset-0 z-50 flex justify-end">
          {/* Backdrop */}
          <div 
            className="absolute inset-0 bg-black/40 backdrop-blur-[2px] transition-opacity" 
            onClick={() => setSelectedIssue(null)}
          />
          
          {/* Drawer */}
          <div className="relative flex h-full w-full max-w-md flex-col bg-surface shadow-2xl animate-in slide-in-from-right duration-300 border-l border-border">
            <div className="flex items-center justify-between border-b border-border px-6 py-5 bg-canvas-soft">
              <div>
                <h2 className="text-xl font-bold">Ariza tafsilotlari #{selectedIssue.id}</h2>
                <div className="mt-1 text-xs text-muted">{new Date(selectedIssue.created_at).toLocaleString()}</div>
              </div>
              <button 
                onClick={() => setSelectedIssue(null)} 
                className="rounded-full p-2 hover:bg-border transition text-muted hover:text-ink"
              >
                <X size={20} />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6 space-y-8">
              {/* Type & Status */}
              <section className="space-y-4">
                <div className="flex justify-between items-center rounded-lg bg-canvas p-3 border border-border">
                  <span className="text-sm text-muted">Muammo turi:</span>
                  <span className="font-semibold text-base">{getTypeLabel(selectedIssue.issue_type)}</span>
                </div>
                
                <div>
                  <label className="text-sm font-semibold mb-2 block">Joriy holat</label>
                  <select 
                    value={selectedIssue.status}
                    onChange={(e) => handleStatusChange(selectedIssue.id, e.target.value as IssueStatus)}
                    className="w-full rounded-input border border-border bg-canvas-soft px-3 py-2.5 text-sm focus:border-accent focus:ring-1 focus:ring-accent outline-none transition"
                  >
                    <option value="new">Yangi</option>
                    <option value="in_progress">Jarayonda</option>
                    <option value="resolved">Hal qilindi</option>
                  </select>
                </div>
              </section>

              {/* Employee & Location */}
              <section className="space-y-4">
                <h3 className="font-semibold text-sm uppercase tracking-wider text-muted">Yuboruvchi</h3>
                {employees[selectedIssue.employee_id] ? (
                  <div className="rounded-xl border border-border bg-canvas p-4 space-y-3">
                    <div>
                      <div className="text-xs text-muted mb-0.5">Xodimning F.I.Sh.</div>
                      <div className="font-medium">{employees[selectedIssue.employee_id].full_name}</div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-xs text-muted mb-0.5">Manzil (Xona)</div>
                        <div className="font-medium">{rooms[employees[selectedIssue.employee_id].room_id]?.name || 'Noma\'lum'}</div>
                      </div>
                      <div>
                        <div className="text-xs text-muted mb-0.5">JShShIR</div>
                        <div className="font-medium text-sm">{employees[selectedIssue.employee_id].jshir}</div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-muted text-sm border border-dashed border-border rounded-lg p-4">Xodim topilmadi</div>
                )}
              </section>

              {/* Inventory */}
              <section className="space-y-4">
                <h3 className="font-semibold text-sm uppercase tracking-wider text-muted flex items-center gap-2">
                  <MonitorSmartphone size={16} />
                  Biriktirilgan inventar
                </h3>
                
                <div className="space-y-3">
                  {inventory.filter(i => i.employee_id === selectedIssue.employee_id).length === 0 ? (
                    <div className="text-sm text-muted text-center p-6 border border-dashed border-border rounded-lg">
                      Ushbu xodimga biriktirilgan inventar yo'q
                    </div>
                  ) : (
                    inventory.filter(i => i.employee_id === selectedIssue.employee_id).map(inv => (
                      <div key={inv.id} className="rounded-lg border border-border bg-surface p-4 flex gap-4 transition hover:border-accent/30">
                        {inv.image_url ? (
                          <img 
                            src={inv.image_url.startsWith('http') ? inv.image_url : `/api${inv.image_url}`}
                            alt={inv.name} 
                            className="w-16 h-16 rounded-md object-cover bg-canvas-soft border border-border flex-shrink-0"
                            onError={(e) => { (e.target as HTMLImageElement).src = 'https://via.placeholder.com/150?text=Rasm+yo\'q' }}
                          />
                        ) : (
                          <div className="w-16 h-16 rounded-md bg-canvas flex items-center justify-center text-muted border border-border flex-shrink-0">
                            <MonitorSmartphone size={24} />
                          </div>
                        )}
                        <div className="flex flex-col justify-center min-w-0">
                          <div className="font-semibold text-sm truncate" title={inv.name}>{inv.name}</div>
                          <div className="text-xs text-muted mt-1 grid grid-cols-1 gap-0.5">
                            {inv.code && <div>Inv. kod: <span className="font-medium text-ink">{inv.code}</span></div>}
                            {inv.ip_address && <div>IP: <span className="font-medium text-ink">{inv.ip_address}</span></div>}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </section>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
