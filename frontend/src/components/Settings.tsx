import { useAuthStore } from '../hooks/useAuthStore'
import { Shield, User, Key, Bell, Eye, EyeOff } from 'lucide-react'

export default function Settings() {
  const { user } = useAuthStore()

  return (
    <div style={{ maxWidth: 800 }}>
      <header style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 28, fontWeight: 600 }}>Settings</h1>
        <p style={{ color: 'var(--fg-secondary)', marginTop: 4 }}>Manage your account and preferences</p>
      </header>

      <div className="card" style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
          <User size={20} /> Account
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 16 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <label style={{ fontSize: 12, color: 'var(--fg-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Email</label>
            <span style={{ fontSize: 16, fontWeight: 500 }}>{user?.email}</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <label style={{ fontSize: 12, color: 'var(--fg-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Username</label>
            <span style={{ fontSize: 16, fontWeight: 500 }}>{user?.username || '—'}</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <label style={{ fontSize: 12, color: 'var(--fg-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Role</label>
            <span className={`badge ${user?.role === 'admin' ? 'badge-error' : user?.role === 'operator' ? 'badge-warning' : 'badge-info'}`}>
              {user?.role}
            </span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <label style={{ fontSize: 12, color: 'var(--fg-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Status</label>
            <span className={`badge ${user?.is_active ? 'badge-success' : 'badge-error'}`}>
              {user?.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Shield size={20} /> Security
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div>
            <h3 style={{ fontSize: 14, fontWeight: 500, marginBottom: 8 }}>Authentication</h3>
            <p style={{ fontSize: 14, color: 'var(--fg-secondary)', marginBottom: 12 }}>
              Currently using demo authentication. In production, configure OIDC with Keycloak.
            </p>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              <span className="badge badge-info">Demo Mode</span>
              <span className="badge" style={{ background: 'var(--border)', color: 'var(--fg-muted)' }}>OIDC Disabled</span>
            </div>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Key size={20} /> API Configuration
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div>
            <h3 style={{ fontSize: 14, fontWeight: 500, marginBottom: 8 }}>LLM Provider Settings</h3>
            <p style={{ fontSize: 14, color: 'var(--fg-secondary)', marginBottom: 12 }}>
              Configure LLM providers in the backend .env file:
            </p>
            <div style={{ fontFamily: 'monospace', fontSize: 13, background: 'var(--bg-tertiary)', padding: '12px', borderRadius: 6, overflow: 'auto' }}>
              <div>LLM_API_KEY=your-api-key</div>
              <div>LLM_PROVIDER=openai-compatible</div>
              <div>LLM_MODEL=gpt-4o-mini</div>
              <div>LLM_BASE_URL=https://api.openai.com/v1</div>
            </div>
          </div>
          <div>
            <h3 style={{ fontSize: 14, fontWeight: 500, marginBottom: 8 }}>Supported Providers</h3>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              <span className="badge badge-info">OpenAI Compatible</span>
              <span className="badge badge-info">Anthropic</span>
              <span className="badge badge-info">Gemini</span>
              <span className="badge badge-info">Ollama</span>
            </div>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Bell size={20} /> Notifications
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer' }}>
            <input type="checkbox" defaultChecked />
            <span>Desktop notifications for attention items</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer' }}>
            <input type="checkbox" />
            <span>Sound alerts</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer' }}>
            <input type="checkbox" />
            <span>Quiet hours (22:00 - 07:00)</span>
          </label>
        </div>
      </div>

      <div className="card">
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Eye size={20} /> Privacy Mode
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer' }}>
            <input type="checkbox" />
            <span>Enable privacy mode (mask sensitive text in panes)</span>
          </label>
          <p style={{ fontSize: 14, color: 'var(--fg-secondary)', marginLeft: 28 }}>
            When enabled, secrets, emails, phone numbers, credit cards, IBANs, and IPs are masked with ████ in the UI.
            Configure custom patterns in backend config.
          </p>
          <div style={{ marginLeft: 28, padding: '12px', background: 'var(--bg-tertiary)', borderRadius: 6, fontFamily: 'monospace', fontSize: 13 }}>
            <div>Built-in rules: secret, email, phone, card, iban, ip</div>
            <div>Allow hosts: github.com, learn.microsoft.com</div>
          </div>
        </div>
      </div>
    </div>
  )
}
