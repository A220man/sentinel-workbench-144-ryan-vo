import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { sessionsApi } from '../api/client'
import type { Session, SessionListResponse } from '../types/api'
import { Plus, Search, Filter, ChevronLeft, ChevronRight } from 'lucide-react'

export default function Sessions() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [spaceFilter, setSpaceFilter] = useState('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showCreate, setShowCreate] = useState(false)
  const [newSessionName, setNewSessionName] = useState('')
  const [newSessionSpace, setNewSessionSpace] = useState('')
  const [spaces, setSpaces] = useState<string[]>([])
  const navigate = useNavigate()

  const fetchSessions = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await sessionsApi.list({ page, page_size: pageSize, space: spaceFilter || undefined })
      setSessions(res.data.items)
      setTotal(res.data.total)
    } catch {
      setError('Failed to load sessions')
    } finally {
      setLoading(false)
    }
  }

  const fetchSpaces = async () => {
    try {
      const res = await sessionsApi.listSpaces()
      setSpaces(res.data)
    } catch {
      // Ignore
    }
  }

  useEffect(() => {
    fetchSessions()
    fetchSpaces()
  }, [page, spaceFilter])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newSessionName.trim()) return
    try {
      await sessionsApi.create({ name: newSessionName.trim(), space: newSessionSpace.trim() || undefined })
      setShowCreate(false)
      setNewSessionName('')
      setNewSessionSpace('')
      fetchSessions()
    } catch {
      setError('Failed to create session')
    }
  }

  const filteredSessions = sessions.filter(s =>
    s.name.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div>
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24, flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h1 style={{ fontSize: 28, fontWeight: 600 }}>Sessions</h1>
          <p style={{ color: 'var(--fg-secondary)', marginTop: 4 }}>Manage your terminal sessions and workspaces</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="btn btn-primary"
        >
          <Plus size={18} /> New Session
        </button>
      </header>

      {error && (
        <div style={{ marginBottom: 16, padding: '12px 16px', background: 'rgba(248, 81, 73, 0.1)', border: '1px solid var(--error)', borderRadius: 8, color: 'var(--error)', display: 'flex', alignItems: 'center', gap: 8 }}>
          {error}
        </div>
      )}

      <div className="card" style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ position: 'relative', flex: 1, minWidth: 200 }}>
            <Search size={18} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--fg-muted)' }} />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search sessions..."
              className="input"
              style={{ paddingLeft: 40 }}
            />
          </div>
          <div style={{ position: 'relative', minWidth: 180 }}>
            <Filter size={18} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--fg-muted)' }} />
            <select
              value={spaceFilter}
              onChange={(e) => { setSpaceFilter(e.target.value); setPage(1); }}
              className="input"
              style={{ paddingLeft: 40 }}
            >
              <option value="">All Spaces</option>
              {spaces.map(space => <option key={space} value={space}>{space}</option>)}
            </select>
          </div>
        </div>
      </div>

      <div className="card">
        {loading ? (
          <div style={{ textAlign: 'center', padding: 48, color: 'var(--fg-secondary)' }}>Loading...</div>
        ) : filteredSessions.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📁</div>
            <p>{search ? 'No sessions match your search' : 'No sessions yet. Create one to get started.'}</p>
          </div>
        ) : (
          <>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th style={{ width: 40 }}>#</th>
                    <th>Name</th>
                    <th>Space</th>
                    <th>Panes</th>
                    <th>Created</th>
                    <th>Updated</th>
                    <th style={{ width: 100 }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredSessions.map((session, idx) => (
                    <tr key={session.id}>
                      <td style={{ color: 'var(--fg-secondary)' }}>{(page - 1) * pageSize + idx + 1}</td>
                      <td>
                        <Link to={`/sessions/${session.id}`} style={{ fontWeight: 500, color: 'var(--fg-primary)' }}>
                          {session.name}
                        </Link>
                      </td>
                      <td>{session.space || <span style={{ color: 'var(--fg-muted)' }}>—</span>}</td>
                      <td>{session.window_count}</td>
                      <td style={{ color: 'var(--fg-secondary)', fontSize: 13 }}>{new Date(session.created_at).toLocaleDateString()}</td>
                      <td style={{ color: 'var(--fg-secondary)', fontSize: 13 }}>{new Date(session.updated_at).toLocaleDateString()}</td>
                      <td>
                        <Link to={`/sessions/${session.id}`} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: 13 }}>
                          View
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {total > pageSize && (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12, marginTop: 16, paddingTop: 16, borderTop: '1px solid var(--border)' }}>
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="btn btn-secondary"
                >
                  <ChevronLeft size={16} />
                </button>
                <span style={{ color: 'var(--fg-secondary)' }}>
                  Page {page} of {Math.ceil(total / pageSize)}
                </span>
                <button
                  onClick={() => setPage(p => Math.min(Math.ceil(total / pageSize), p + 1))}
                  disabled={page === Math.ceil(total / pageSize)}
                  className="btn btn-secondary"
                >
                  <ChevronRight size={16} />
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {showCreate && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, padding: 24 }}>
          <div className="card" style={{ width: '100%', maxWidth: 480 }}>
            <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 16 }}>Create Session</h2>
            <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div>
                <label htmlFor="name" style={{ display: 'block', fontSize: 14, fontWeight: 500, marginBottom: 6 }}>
                  Name
                </label>
                <input
                  id="name"
                  type="text"
                  value={newSessionName}
                  onChange={(e) => setNewSessionName(e.target.value)}
                  required
                  className="input"
                  placeholder="my-session"
                  autoFocus
                />
              </div>
              <div>
                <label htmlFor="space" style={{ display: 'block', fontSize: 14, fontWeight: 500, marginBottom: 6 }}>
                  Space (optional)
                </label>
                <input
                  id="space"
                  type="text"
                  value={newSessionSpace}
                  onChange={(e) => setNewSessionSpace(e.target.value)}
                  className="input"
                  placeholder="backend, frontend, etc."
                  list="spaces"
                />
                <datalist id="spaces">
                  {spaces.map(space => <option key={space} value={space} />)}
                </datalist>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
                <button type="button" onClick={() => setShowCreate(false)} className="btn btn-secondary">Cancel</button>
                <button type="submit" className="btn btn-primary">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
