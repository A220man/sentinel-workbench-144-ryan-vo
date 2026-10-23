import { useEffect, useState } from 'react'
import { sessionsApi, windowsApi, attentionApi } from '../api/client'
import type { Session, Window, AttentionSummary } from '../types/api'
import { LayoutGrid, Monitor, Inbox, AlertTriangle, CheckCircle, HelpCircle, XCircle } from 'lucide-react'

export default function Dashboard() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [windows, setWindows] = useState<Window[]>([])
  const [attentionSummary, setAttentionSummary] = useState<AttentionSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchData = async () => {
    try {
      setLoading(true)
      const [sessionsRes, windowsRes, attentionRes] = await Promise.all([
        sessionsApi.list({ page_size: 10 }),
        windowsApi.list({ page_size: 20 }),
        attentionApi.summary(),
      ])
      setSessions(sessionsRes.data.items)
      setWindows(windowsRes.data.items)
      setAttentionSummary(attentionRes.data)
    } catch (err) {
      setError('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const totalWindows = windows.length
  const workingWindows = windows.filter(w => w.agent_state === 'working').length
  const doneWindows = windows.filter(w => w.agent_state === 'done').length
  const errorWindows = windows.filter(w => w.agent_state === 'errored').length
  const needsInputWindows = windows.filter(w => w.agent_state === 'needs_input').length

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '400px' }}>
        <div className="animate-spin" style={{ fontSize: 24, color: 'var(--accent)' }}>⟳</div>
      </div>
    )
  }

  const statCards = [
    { label: 'Sessions', value: sessions.length, icon: LayoutGrid, color: 'var(--accent)' },
    { label: 'Total Panes', value: totalWindows, icon: Monitor, color: 'var(--success)' },
    { label: 'Working', value: workingWindows, icon: CheckCircle, color: 'var(--warning)' },
    { label: 'Inbox Items', value: attentionSummary?.total || 0, icon: Inbox, color: 'var(--error)' },
  ]

  return (
    <div>
      <header style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 28, fontWeight: 600 }}>Dashboard</h1>
        <p style={{ color: 'var(--fg-secondary)', marginTop: 4 }}>Overview of your agent sessions and panes</p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 32 }}>
        {statCards.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="card" style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: 14, color: 'var(--fg-secondary)' }}>{label}</span>
              <Icon size={20} style={{ color }} />
            </div>
            <div style={{ fontSize: 36, fontWeight: 700 }}>{value}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 16 }}>
        <div className="card">
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Recent Sessions</h2>
          {sessions.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">📁</div>
              <p>No sessions yet. Create one to get started.</p>
            </div>
          ) : (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Space</th>
                    <th>Panes</th>
                    <th>Updated</th>
                  </tr>
                </thead>
                <tbody>
                  {sessions.slice(0, 5).map((session) => (
                    <tr key={session.id}>
                      <td style={{ fontWeight: 500 }}>{session.name}</td>
                      <td>{session.space || <span style={{ color: 'var(--fg-muted)' }}>—</span>}</td>
                      <td>{session.window_count}</td>
                      <td style={{ color: 'var(--fg-secondary)', fontSize: 13 }}>
                        {new Date(session.updated_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="card">
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Agent States</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <StateRow label="Working" count={workingWindows} icon={CheckCircle} color="var(--warning)" />
            <StateRow label="Done" count={doneWindows} icon={CheckCircle} color="var(--success)" />
            <StateRow label="Needs Input" count={needsInputWindows} icon={HelpCircle} color="var(--accent)" />
            <StateRow label="Errored" count={errorWindows} icon={XCircle} color="var(--error)" />
            <StateRow label="Idle/Unknown" count={totalWindows - workingWindows - doneWindows - needsInputWindows - errorWindows} icon={Monitor} color="var(--fg-secondary)" />
          </div>
        </div>

        <div className="card" style={{ gridColumn: '1 / -1' }}>
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Inbox Summary</h2>
          {attentionSummary ? (
            <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
              <AttentionStat kind="finished" label="Finished" count={attentionSummary.by_kind.finished || 0} icon={CheckCircle} color="var(--success)" />
              <AttentionStat kind="question" label="Questions" count={attentionSummary.by_kind.question || 0} icon={HelpCircle} color="var(--accent)" />
              <AttentionStat kind="errored" label="Errored" count={attentionSummary.by_kind.errored || 0} icon={XCircle} color="var(--error)" />
              <AttentionStat kind="approval" label="Approvals" count={attentionSummary.by_kind.approval || 0} icon={AlertTriangle} color="var(--warning)" />
            </div>
          ) : (
            <p style={{ color: 'var(--fg-secondary)' }}>No attention data</p>
          )}
        </div>
      </div>
    </div>
  )
}

function StateRow({ label, count, icon: Icon, color }: { label: string; count: number; icon: React.ComponentType<{ size?: number }>; color: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
      <Icon size={18} style={{ color }} />
      <span style={{ flex: 1 }}>{label}</span>
      <span style={{ fontWeight: 600, fontSize: 18, color }}>{count}</span>
    </div>
  )
}

function AttentionStat({ label, count, icon: Icon, color }: { label: string; count: number; icon: React.ComponentType<{ size?: number }>; color: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '12px 16px', background: 'var(--bg-tertiary)', borderRadius: 8 }}>
      <Icon size={18} style={{ color }} />
      <div>
        <div style={{ fontSize: 13, color: 'var(--fg-secondary)' }}>{label}</div>
        <div style={{ fontWeight: 600, fontSize: 18, color }}>{count}</div>
      </div>
    </div>
  )
}
