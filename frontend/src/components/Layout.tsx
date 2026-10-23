import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../hooks/useAuthStore'
import { LayoutDashboard, LayoutGrid, Inbox, Settings, LogOut, User } from 'lucide-react'

export default function Layout() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/sessions', label: 'Sessions', icon: LayoutGrid },
    { path: '/inbox', label: 'Inbox', icon: Inbox },
    { path: '/settings', label: 'Settings', icon: Settings },
  ]

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <aside style={{
        width: 260,
        background: 'var(--bg-secondary)',
        borderRight: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        padding: '16px',
        gap: 8,
      }}>
        <div style={{ padding: '16px 8px', borderBottom: '1px solid var(--border)', marginBottom: 8 }}>
          <h1 style={{ fontSize: 18, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 24 }}>🛡️</span>
            Sentinel Workbench
          </h1>
          <p style={{ fontSize: 12, color: 'var(--fg-secondary)', marginTop: 4 }}>v1.0.0</p>
        </div>
        
        <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 4 }}>
          {navItems.map(({ path, label, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                padding: '10px 12px',
                borderRadius: 8,
                color: isActive ? 'var(--accent)' : 'var(--fg-secondary)',
                background: isActive ? 'rgba(88, 166, 255, 0.1)' : 'transparent',
                fontWeight: isActive ? 600 : 400,
                textDecoration: 'none',
                transition: 'all 0.15s ease',
              })}
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div style={{ borderTop: '1px solid var(--border)', paddingTop: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '8px 12px' }}>
            <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 600, fontSize: 14 }}>
              {user?.email?.[0]?.toUpperCase() || 'U'}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 14, fontWeight: 500, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {user?.username || user?.email}
              </div>
              <div style={{ fontSize: 12, color: 'var(--fg-secondary)', textTransform: 'capitalize' }}>
                {user?.role}
              </div>
            </div>
          </div>
          <button
            onClick={handleLogout}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 12,
              padding: '10px 12px',
              borderRadius: 8,
              border: '1px solid var(--border)',
              background: 'transparent',
              color: 'var(--fg-secondary)',
              fontSize: 14,
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--error)'; e.currentTarget.style.borderColor = 'var(--error)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--fg-secondary)'; e.currentTarget.style.borderColor = 'var(--border)'; }}
          >
            <LogOut size={18} />
            Sign Out
          </button>
        </div>
      </aside>

      <main style={{ flex: 1, padding: '24px', overflow: 'auto' }}>
        <Outlet />
      </main>
    </div>
  )
}
