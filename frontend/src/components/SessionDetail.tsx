import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { sessionsApi, windowsApi } from '../api/client'
import type { Session, Window } from '../types/api'
import { Plus, ArrowRightLeft, Trash2, Edit2, Loader2, Bell, BellOff } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

export default function SessionDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [session, setSession] = useState<Session | null>(null)
  const [windows, setWindows] = useState<Window[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showCreateWindow, setShowCreateWindow] = useState(false)
  const [newWindowTitle, setNewWindowTitle] = useState('')
  const [newWindowWorkspace, setNewWindowWorkspace] = useState(1)
  const [newWindowIndex, setNewWindowIndex] = useState(0)

  const fetchData = async () => {
    if (!id) return
    setLoading(true)
    setError('')
    try {
      const [sessionRes, windowsRes] = await Promise.all([
        sessionsApi.get(parseInt(id)),
        windowsApi.list({ session_id: parseInt(id) }),
      ])
      setSession(sessionRes.data)
      setWindows(windowsRes.data.items)
    } catch {
      setError('Failed to load session')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [id])

  const handleCreateWindow = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!id) return
    try {
      await windowsApi.create({
        session_id: parseInt(id),
        workspace: newWindowWorkspace,
        index: newWindowIndex,
        title: newWindowTitle.trim() || undefined,
      })
      setShowCreateWindow(false)
      setNewWindowTitle('')
      fetchData()
    } catch {
      setError('Failed to create window')
    }
  }

  const handleDeleteWindow = async (windowId: number) => {
    if (!confirm('Delete this window?')) return
    try {
      await windowsApi.delete(windowId)
      fetchData()
    } catch {
      setError('Failed to delete window')
    }
  }

  const handleToggleQuiet = async (window: Window) => {
    try {
      await windowsApi.setQuiet(window.id, !window.quiet)
      fetchData()
    } catch {
      setError('Failed to toggle quiet mode')
    }
  }

  const handleMoveWindow = async (window: Window, toSessionId: number) => {
    try {
      await windowsApi.move(window.id, toSessionId, 1, 0)
      fetchData()
    } catch {
      setError('Failed to move window')
    }
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px' }}>
        <Loader2 size={32} className="animate-spin" style={{ color: 'var(--accent)' }} />
      </div>
    )
  }

  if (!session) {
    return (
      <div className="empty-state" style={{ minHeight: '400px' }}>
        <div className="empty-state-icon">⚠️</div>
        <p>{error || 'Session not found'}</p>
        <button onClick={() => navigate('/sessions')} className="btn btn-primary" style={{ marginTop: 16 }}>
          Back to Sessions
        </button>
      </div>
    )
  }

  const getStateBadge = (state: Window['agent_state']) => {
    const badges: Record<string, { label: string; class: string; icon: React.ComponentType<{ size?: number }> }> = {
      working: { label: 'Working', class: 'badge-warning', icon: Loader2 },
      done: { label: 'Done', class: 'badge-success', icon: CheckCircle },
      needs_input: { label: 'Needs Input', class: 'badge-info', icon: HelpCircle },
      errored: { label: 'Errored', class: 'badge-error', icon: XCircle },
      idle: { label: 'Idle', class: 'badge-info', icon: Monitor },
      unknown: { label: 'Unknown', class: '', icon: Monitor },
    }
    const b = badges[state] || badges.unknown
    return <span className={`badge ${b.class}`}><b.icon size={12} /> {b.label}</span>
  }

  return (
    <div>
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24, flexWrap: 'wrap', gap: 16 }}>
        <div>
          <button onClick={() => navigate('/sessions')} className="btn btn-secondary" style={{ marginBottom: 12 }}>
            ← Back
          </button>
          <h1 style={{ fontSize: 28, fontWeight: 600 }}>{session.name}</h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 8, flexWrap: 'wrap' }}>
            {session.space && (
              <span className="badge badge-info">📁 {session.space}</span>
            )}
            <span style={{ color: 'var(--fg-secondary)', fontSize: 14 }}>
              {session.window_count} pane(s) • Updated {formatDistanceToNow(new Date(session.updated_at), { addSuffix: true })}
            </span>
          </div>
        </div>
        <button
          onClick={() => setShowCreateWindow(true)}
          className="btn btn-primary"
        >
          <Plus size={18} /> Add Pane
        </button>
      </header>

      {error && (
        <div style={{ marginBottom: 16, padding: '12px 16px', background: 'rgba(248, 81, 73, 0.1)', border: '1px solid var(--error)', borderRadius: 8, color: 'var(--error)' }}>
          {error}
        </div>
      )}

      <div className="card">
        {windows.length === 0 ? (
          <div className="empty-state" style={{ minHeight: '300px' }}>
            <div className="empty-state-icon">🖥️</div>
            <p>No panes in this session. Add one to get started.</p>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th style={{ width: 50 }}>#</th>
                  <th>Title</th>
                  <th>Workspace</th>
                  <th>State</th>
                  <th>Quiet</th>
                  <th>Completions</th>
                  <th>Command</th>
                  <th>CWD</th>
                  <th style={{ width: 160 }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {windows.map((window) => (
                  <tr key={window.id}>
                    <td style={{ color: 'var(--fg-secondary)' }}>{window.index + 1}</td>
                    <td style={{ fontWeight: 500, maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {window.title || <span style={{ color: 'var(--fg-muted)' }}>—</span>}
                    </td>
                    <td>{window.workspace}</td>
                    <td>{getStateBadge(window.agent_state)}</td>
                    <td>
                      <button
                        onClick={() => handleToggleQuiet(window)}
                        className={`btn ${window.quiet ? 'btn-primary' : 'btn-secondary'}`}
                        style={{ padding: '4px 10px', fontSize: 12 }}
                        title={window.quiet ? 'Disable quiet mode' : 'Enable quiet mode'}
                      >
                        <BellOff size={12} style={{ display: window.quiet ? 'inline' : 'none' }} />
                        <Bell size={12} style={{ display: window.quiet ? 'none' : 'inline' }} />
                        {window.quiet ? ' Quiet' : ' Active'}
                      </button>
                    </td>
                    <td>{window.completion_seq}</td>
                    <td style={{ fontFamily: 'monospace', fontSize: 12, color: 'var(--fg-secondary)', maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {window.command || <span style={{ color: 'var(--fg-muted)' }}>—</span>}
                    </td>
                    <td style={{ fontFamily: 'monospace', fontSize: 12, color: 'var(--fg-secondary)', maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {window.cwd || <span style={{ color: 'var(--fg-muted)' }}>—</span>}
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: 8 }}>
                        <button
                          onClick={() => handleMoveWindow(window, 0)} // Would need session picker
                          className="btn btn-secondary"
                          style={{ padding: '4px 8px', fontSize: 12 }}
                          title="Move to another session"
                        >
                          <ArrowRightLeft size={12} />
                        </button>
                        <button
                          onClick={() => handleDeleteWindow(window.id)}
                          className="btn btn-danger"
                          style={{ padding: '4px 8px', fontSize: 12 }}
                        >
                          <Trash2 size={12} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showCreateWindow && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, padding: 24 }}>
          <div className="card" style={{ width: '100%', maxWidth: 480 }}>
            <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 16 }}>Add Pane</h2>
            <form onSubmit={handleCreateWindow} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div>
                <label htmlFor="title" style={{ display: 'block', fontSize: 14, fontWeight: 500, marginBottom: 6 }}>
                  Title (optional)
                </label>
                <input
                  id="title"
                  type="text"
                  value={newWindowTitle}
                  onChange={(e) => setNewWindowTitle(e.target.value)}
                  className="input"
                  placeholder="my-task"
                />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                <div>
                  <label htmlFor="workspace" style={{ display: 'block', fontSize: 14, fontWeight: 500, marginBottom: 6 }}>
                    Workspace (1-9)
                  </label>
                  <input
                    id="workspace"
                    type="number"
                    value={newWindowWorkspace}
                    onChange={(e) => setNewWindowWorkspace(Math.max(1, Math.min(9, parseInt(e.target.value) || 1)))}
                    min={1}
                    max={9}
                    className="input"
                  />
                </div>
                <div>
                  <label htmlFor="index" style={{ display: 'block', fontSize: 14, fontWeight: 500, marginBottom: 6 }}>
                    Index
                  </label>
                  <input
                    id="index"
                    type="number"
                    value={newWindowIndex}
                    onChange={(e) => setNewWindowIndex(Math.max(0, parseInt(e.target.value) || 0))}
                    min={0}
                    className="input"
                  />
                </div>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
                <button type="button" onClick={() => setShowCreateWindow(false)} className="btn btn-secondary">Cancel</button>
                <button type="submit" className="btn btn-primary">Add</button>
              </div>
            </form>
          </div>
        </div>
      )}
    )
  }
}

// Missing imports - add at top
import { CheckCircle, HelpCircle, XCircle, Monitor } from 'lucide-react'
