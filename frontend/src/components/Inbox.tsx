import { useEffect, useState } from 'react'
import { attentionApi } from '../api/client'
import type { AttentionItem, AttentionKind } from '../types/api'
import { X, CheckCircle, HelpCircle, AlertTriangle, Loader2, ChevronLeft, ChevronRight } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

export default function Inbox() {
  const [items, setItems] = useState<AttentionItem[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [kindFilter, setKindFilter] = useState<AttentionKind | ''>('')
  const [showDismissed, setShowDismissed] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [dismissing, setDismissing] = useState<Record<number, boolean>>({})

  const fetchItems = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await attentionApi.list({
        kind: kindFilter || undefined,
        dismissed: showDismissed,
        page,
        page_size: pageSize,
      })
      setItems(res.data.items)
      setTotal(res.data.total)
    } catch {
      setError('Failed to load inbox')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchItems()
  }, [page, kindFilter, showDismissed])

  const handleDismiss = async (item: AttentionItem) => {
    const nonce = prompt('Enter human nonce to dismiss:')
    if (!nonce) return
    
    setDismissing(prev => ({ ...prev, [item.id]: true }))
    try {
      await attentionApi.dismiss(item.id, nonce)
      fetchItems()
    } catch {
      setError('Failed to dismiss item')
    } finally {
      setDismissing(prev => ({ ...prev, [item.id]: false }))
    }
  }

  const getKindBadge = (kind: AttentionKind) => {
    const badges: Record<AttentionKind, { label: string; class: string; icon: React.ComponentType<{ size?: number }> }> = {
      finished: { label: 'Finished', class: 'badge-success', icon: CheckCircle },
      question: { label: 'Question', class: 'badge-info', icon: HelpCircle },
      errored: { label: 'Errored', class: 'badge-error', icon: AlertTriangle },
      approval: { label: 'Approval', class: 'badge-warning', icon: AlertTriangle },
    }
    const b = badges[kind]
    return <span className={`badge ${b.class}`}><b.icon size={12} /> {b.label}</span>
  }

  return (
    <div>
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24, flexWrap: 'wrap', gap: 16 }}>
        <div>
          <h1 style={{ fontSize: 28, fontWeight: 600 }}>Inbox</h1>
          <p style={{ color: 'var(--fg-secondary)', marginTop: 4 }}>Attention items from your agent panes</p>
        </div>
      </header>

      {error && (
        <div style={{ marginBottom: 16, padding: '12px 16px', background: 'rgba(248, 81, 73, 0.1)', border: '1px solid var(--error)', borderRadius: 8, color: 'var(--error)' }}>
          {error}
        </div>
      )}

      <div className="card" style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ display: 'flex', gap: 8 }}>
            {(['finished', 'question', 'errored', 'approval'] as AttentionKind[]).map(kind => (
              <button
                key={kind}
                onClick={() => { setKindFilter(k => k === kind ? '' : kind); setPage(1); }}
                className={`btn ${kindFilter === kind ? 'btn-primary' : 'btn-secondary'}`}
                style={{ padding: '6px 12px', fontSize: 13 }}
              >
                {kind.charAt(0).toUpperCase() + kind.slice(1)}
              </button>
            ))}
          </div>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 14, cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={showDismissed}
              onChange={(e) => { setShowDismissed(e.target.checked); setPage(1); }}
            />
            Show dismissed
          </label>
        </div>
      </div>

      <div className="card">
        {loading ? (
          <div style={{ textAlign: 'center', padding: 48, color: 'var(--fg-secondary)' }}>
            <Loader2 size={24} className="animate-spin" style={{ color: 'var(--accent)' }} />
          </div>
        ) : items.length === 0 ? (
          <div className="empty-state" style={{ minHeight: '300px' }}>
            <div className="empty-state-icon">📭</div>
            <p>{kindFilter ? `No ${kindFilter} items` : 'Inbox is empty'}</p>
          </div>
        ) : (
          <>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th style={{ width: 50 }}>#</th>
                    <th>Kind</th>
                    <th>Title</th>
                    <th>Session</th>
                    <th>Pane</th>
                    <th>Created</th>
                    <th style={{ width: 120 }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((item, idx) => (
                    <tr key={item.id} style={{ opacity: item.dismissed_at ? 0.5 : 1 }}>
                      <td style={{ color: 'var(--fg-secondary)' }}>{(page - 1) * pageSize + idx + 1}</td>
                      <td>{getKindBadge(item.kind)}</td>
                      <td style={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {item.title}
                      </td>
                      <td>{item.session_name}</td>
                      <td style={{ maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {item.window_title || <span style={{ color: 'var(--fg-muted)' }}>—</span>}
                      </td>
                      <td style={{ color: 'var(--fg-secondary)', fontSize: 13 }}>
                        {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
                      </td>
                      <td>
                        {item.dismissed_at ? (
                          <span className="badge" style={{ background: 'var(--border)', color: 'var(--fg-muted)' }}>Dismissed</span>
                        ) : (
                          <button
                            onClick={() => handleDismiss(item)}
                            disabled={dismissing[item.id]}
                            className="btn btn-danger"
                            style={{ padding: '6px 12px', fontSize: 13 }}
                          >
                            {dismissing[item.id] ? <Loader2 size={14} className="animate-spin" /> : 'Dismiss'}
                          </button>
                        )}
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
    </div>
  )
}
