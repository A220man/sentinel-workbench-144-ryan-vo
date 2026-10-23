import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../hooks/useAuthStore'
import { Shield, AlertCircle } from 'lucide-react'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const login = useAuthStore((s) => s.login)
  const navigate = useNavigate()
  const location = useLocation()

  const from = (location.state as { from?: Location })?.from?.pathname || '/'

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate(from, { replace: true })
    } catch {
      setError('Invalid email or password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', padding: '24px' }}>
      <div style={{ width: '100%', maxWidth: 400 }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <Shield size={48} style={{ color: 'var(--accent)', marginBottom: 16 }} />
          <h1 style={{ fontSize: 28, fontWeight: 600, marginBottom: 8 }}>Sentinel Workbench</h1>
          <p style={{ color: 'var(--fg-secondary)' }}>Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {error && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              padding: '12px',
              background: 'rgba(248, 81, 73, 0.1)',
              border: '1px solid var(--error)',
              borderRadius: 8,
              color: 'var(--error)',
              fontSize: 14,
            }}>
              <AlertCircle size={16} />
              {error}
            </div>
          )}

          <div>
            <label htmlFor="email" style={{ display: 'block', fontSize: 14, fontWeight: 500, marginBottom: 6 }}>
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              className="input"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label htmlFor="password" style={{ display: 'block', fontSize: 14, fontWeight: 500, marginBottom: 6 }}>
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              className="input"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{ width: '100%', padding: '12px' }}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p style={{ marginTop: 24, textAlign: 'center', fontSize: 14, color: 'var(--fg-secondary)' }}>
          Demo mode: any email/password works
        </p>
      </div>
    </div>
  )
}
