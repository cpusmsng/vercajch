import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../services/api'
import type { User, AuthToken } from '../types'

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
  setTokens: (accessToken: string, refreshToken: string) => void
  hasPermission: (permission: string) => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: true,

      login: async (email: string, password: string) => {
        const formData = new FormData()
        formData.append('username', email)
        formData.append('password', password)

        const response = await api.post<AuthToken>('/auth/login', formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        })

        const { access_token, refresh_token } = response.data
        set({
          accessToken: access_token,
          refreshToken: refresh_token,
          isAuthenticated: true,
        })

        await get().fetchUser()
      },

      logout: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        })
      },

      fetchUser: async () => {
        try {
          const response = await api.get<User>('/auth/me')
          set({ user: response.data, isLoading: false })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      setTokens: (accessToken: string, refreshToken: string) => {
        set({ accessToken, refreshToken })
      },

      hasPermission: (permission: string) => {
        const user = get().user
        if (!user || !user.permissions) return false
        return user.permissions.includes(permission)
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)

// Initialize auth state on app load
const initAuth = async () => {
  const { accessToken, fetchUser } = useAuthStore.getState()
  if (accessToken) {
    try {
      await fetchUser()
    } catch {
      useAuthStore.getState().logout()
    }
  } else {
    useAuthStore.setState({ isLoading: false })
  }
}

initAuth()
