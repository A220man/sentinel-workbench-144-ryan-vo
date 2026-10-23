import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { vi } from 'vitest'
import Sessions from './Sessions'
import { sessionsApi } from '../api/client'

vi.mock('../api/client')

describe('Sessions', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    sessionsApi.list.mockResolvedValue({ data: { items: [], total: 0 } })
    sessionsApi.listSpaces.mockResolvedValue({ data: [] })
  })

  it('renders sessions list', () => {
    render(
      <BrowserRouter>
        <Sessions />
      </BrowserRouter>
    )
    expect(screen.getByText('Sessions')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /New Session/i })).toBeInTheDocument()
  })

  it('shows empty state when no sessions', async () => {
    render(
      <BrowserRouter>
        <Sessions />
      </BrowserRouter>
    )
    await waitFor(() => {
      expect(screen.getByText('No sessions yet')).toBeInTheDocument()
    })
  })

  it('opens create modal on button click', async () => {
    render(
      <BrowserRouter>
        <Sessions />
      </BrowserRouter>
    )
    fireEvent.click(screen.getByRole('button', { name: /New Session/i }))
    await waitFor(() => {
      expect(screen.getByText('Create Session')).toBeInTheDocument()
    })
  })
})
