import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { vi } from 'vitest'
import Dashboard from './Dashboard'
import { sessionsApi, windowsApi, attentionApi } from '../api/client'

vi.mock('../api/client')

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows loading state initially', () => {
    sessionsApi.list.mockResolvedValue({ data: { items: [], total: 0 } })
    windowsApi.list.mockResolvedValue({ data: { items: [], total: 0 } })
    attentionApi.summary.mockResolvedValue({ data: { total: 0, by_kind: {} } })
    
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders dashboard with stats', async () => {
    sessionsApi.list.mockResolvedValue({ 
      data: { items: [{ id: 1, name: 'Test', space: '', created_at: '', updated_at: '', window_count: 2 }], total: 1 } 
    })
    windowsApi.list.mockResolvedValue({ 
      data: { 
        items: [
          { id: 1, session_id: 1, workspace: 1, index: 0, agent_state: 'working', title: null, command: null, cwd: null, completion_seq: 0, quiet: false, created_at: '', updated_at: '' },
          { id: 2, session_id: 1, workspace: 1, index: 1, agent_state: 'done', title: null, command: null, cwd: null, completion_seq: 1, quiet: false, created_at: '', updated_at: '' },
        ], total: 2 } 
    })
    attentionApi.summary.mockResolvedValue({ data: { total: 1, by_kind: { finished: 1 } } })
    
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument()
    })
    await waitFor(() => {
      expect(screen.getByText('Test')).toBeInTheDocument()
    })
  })
})
