import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import { api, setToken, clearToken } from '../api/client'
import { useTelegram } from '../hooks/useTelegram'
import type { AuthUser } from '../types'

interface AuthContextValue {
  user: AuthUser | null
  loading: boolean
  login: () => Promise<void>
  logout: () => void
  setUser: (u: AuthUser | null) => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)
  const { getInitData, getUser } = useTelegram()

  const login = async () => {
    const initData = getInitData()
    const tgUser = getUser()

    if (!initData) {
      setLoading(false)
      return
    }

    try {
      const data = await api.post<{ token: string; user: AuthUser }>('/auth/telegram', {
        init_data: initData,
      })

      setToken(data.token)

      const enrichedUser: AuthUser = {
        ...data.user,
        photo_url: data.user.photo_url || tgUser?.photo_url,
        first_name: data.user.first_name || tgUser?.first_name,
        last_name: data.user.last_name || tgUser?.last_name,
        username: data.user.username || tgUser?.username,
        language_code: data.user.language_code || tgUser?.language_code,
        telegram_id: data.user.telegram_id || tgUser?.id,
      }
      setUser(enrichedUser)
    } catch {
      setLoading(false)
    }
  }

  const logout = () => {
    clearToken()
    setUser(null)
  }

  // Try to restore session from stored token
  useEffect(() => {
    const token = localStorage.getItem('scripthub_token')
    if (!token) {
      setLoading(false)
      return
    }
    // Try to fetch current user from token
    api.get<{ user: AuthUser }>('/auth/me').then((data) => {
      setUser(data.user)
    }).catch(() => {
      // Token might be expired — try Telegram login
      login()
    })
  }, [])

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
