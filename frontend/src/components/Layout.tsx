import { useState } from 'react'
import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { Building2, LogOut, Menu, X, AlertCircle, Users } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

function navClass({ isActive }: { isActive: boolean }) {
  return `flex items-center gap-2.5 rounded-input px-3 py-2 text-sm font-medium transition ${
    isActive ? 'bg-accent-soft text-accent' : 'text-muted hover:bg-canvas-soft hover:text-ink'
  }`
}

export function Layout() {
  const { logout } = useAuth()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  const sidebar = (
    <div className="flex h-full flex-col">
      <Link to="/faculties" className="flex items-center gap-2 px-2 py-1">
        <span className="grid h-8 w-8 place-items-center rounded-input bg-accent text-sm font-bold text-white">
          R
        </span>
        <span className="text-lg font-semibold text-ink">RRTM</span>
      </Link>

      <nav className="mt-6 flex-1 space-y-1">
        <NavLink to="/faculties" className={navClass} onClick={() => setOpen(false)}>
          <Building2 size={17} />
          Fakultetlar
        </NavLink>
        <NavLink to="/issues" className={navClass} onClick={() => setOpen(false)}>
          <AlertCircle size={17} />
          Arizalar
        </NavLink>
        <NavLink to="/workers" className={navClass} onClick={() => setOpen(false)}>
          <Users size={17} />
          Ishchilar
        </NavLink>
      </nav>

      <button
        onClick={handleLogout}
        className="flex items-center gap-2.5 rounded-input px-3 py-2 text-sm font-medium text-muted transition hover:bg-canvas-soft hover:text-danger"
      >
        <LogOut size={17} />
        Chiqish
      </button>
    </div>
  )

  return (
    <div className="min-h-screen bg-canvas-warm text-ink">
      {/* Desktop sidebar */}
      <aside className="fixed inset-y-0 left-0 hidden w-60 border-r border-border bg-surface p-4 lg:block">
        {sidebar}
      </aside>

      {/* Mobile drawer */}
      {open && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 bg-black/20" onClick={() => setOpen(false)} />
          <aside className="absolute inset-y-0 left-0 w-60 border-r border-border bg-surface p-4">
            {sidebar}
          </aside>
        </div>
      )}

      <div className="lg:pl-60">
        {/* Mobile top bar */}
        <header className="flex items-center gap-3 border-b border-border bg-surface px-4 py-3 lg:hidden">
          <button onClick={() => setOpen((v) => !v)} className="text-muted">
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
          <span className="font-semibold">RRTM</span>
        </header>

        <main className="mx-auto max-w-5xl px-5 py-8 sm:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
