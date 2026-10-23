import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi } from '../api/client'
import type { User } from '../types/api'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  checkAuth: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await authApi.login({ email, password })
          const { access_token } = response.data
          localStorage.setItem('access_token', access_token)
          
          // Fetch user info
          const userResponse = await authApi.me()
          set({
            user: userResponse.data,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (err: unknown) {
          const message = err instanceof Error ? err.message : 'Login failed'
          set({ error: message, isLoading: false, isAuthenticated: false, user: null })
          throw err
        }
      },

      logout: async () => {
        try {
          await authApi.logout()
        } catch {
          // Ignore logout errors
        } finally {
          localStorage.removeItem('access_token')
          set({ user: null, isAuthenticated: false })
        }
      },

      checkAuth: async () => {
        const token = localStorage.getItem('access_token')
        if (!token) {
          set({ isAuthenticated: false, user: null, isLoading: false })
          return
        }
        
        set({ isLoading: true })
        try {
          const response = await authApi.me()
          set({ user: response.data, isAuthenticated: true, isLoading: false })
        } catch {
          localStorage.removeItem('access_token')
          set({ user: null, isAuthenticated: false, isLoading: false })
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)
