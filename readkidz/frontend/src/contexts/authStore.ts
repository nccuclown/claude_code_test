import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User, Credits } from '@/types'
import { api } from '@/services/api'

interface AuthState {
  user: User | null
  credits: Credits | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  // Actions
  login: (email: string, password: string) => Promise<void>
  loginWithGoogle: () => void
  logout: () => void
  fetchCredits: () => Promise<void>
  setToken: (token: string) => void
  setUser: (user: User) => void
  clearError: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      credits: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          const formData = new URLSearchParams()
          formData.append('username', email)
          formData.append('password', password)

          const response = await api.post('/auth/login', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          })

          const { access_token, user } = response.data
          set({
            token: access_token,
            user,
            isAuthenticated: true,
            isLoading: false,
          })

          // Fetch credits after login
          await get().fetchCredits()
        } catch (error: unknown) {
          const errorMessage = error instanceof Error ? error.message : 'Login failed'
          set({ error: errorMessage, isLoading: false })
          throw error
        }
      },

      loginWithGoogle: () => {
        // Redirect to Google OAuth
        window.location.href = '/api/v1/auth/google'
      },

      logout: () => {
        set({
          user: null,
          credits: null,
          token: null,
          isAuthenticated: false,
          error: null,
        })
      },

      fetchCredits: async () => {
        try {
          const response = await api.get('/auth/me/credits')
          set({ credits: response.data })
        } catch (error) {
          console.error('Failed to fetch credits:', error)
        }
      },

      setToken: (token: string) => {
        set({ token, isAuthenticated: true })
      },

      setUser: (user: User) => {
        set({ user })
      },

      clearError: () => {
        set({ error: null })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
