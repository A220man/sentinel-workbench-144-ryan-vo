import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { vi } from 'vitest'
import Login from './Login'
import { useAuthStore } from '../hooks/useAuthStore'

vi.mock('../hooks/useAuthStore')

describe('Login', () => {
  const mockLogin = vi.fn()
  
  beforeEach(() => {
    vi.clearAllMocks()
    ;(useAuthStore as unknown as { getState: () => { login: ReturnType<typeof vi.fn> } }).getState = () => ({
      login: mockLogin,
    })
  })

  it('renders login form', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )
    expect(screen.getByLabelText('Email')).toBeInTheDocument()
    expect(screen.getByLabelText('Password')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument()
  })

  it('shows error on failed login', async () => {
    mockLogin.mockRejectedValueOnce(new Error('Invalid credentials'))
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    )
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'test@example.com' } })
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'wrong' } })
    fireEvent.click(screen.getByRole('button', { name: 'Sign In' }))
    await waitFor(() => {
      expect(screen.getByText('Invalid email or password')).toBeInTheDocument()
    })
  })
})
