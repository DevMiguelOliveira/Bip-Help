import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import type { User } from '../types'
import { getMe, login as loginRequest } from '../services/auth'
import { setUnauthorizedHandler, setCurrentUserRole } from '../lib/api'

interface AuthContextValue {
  token: string | null
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)
const TOKEN_KEY = 'bip-access-token'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    setToken(null)
    setUser(null)
  }, [])

  useEffect(() => {
    setUnauthorizedHandler(logout)

    if (!token) {
      setLoading(false)
      return
    }

    let cancelled = false

    getMe(token)
      .then((current) => {
        if (!cancelled) {
          setUser(current)
          setCurrentUserRole(current.perfil_sistema)
        }
      })
      .catch(() => {
        if (!cancelled) logout()
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [token, logout])

  const refreshUser = useCallback(async () => {
    if (!token) return
    const current = await getMe(token)
    setUser(current)
  }, [token])

  const login = useCallback(async (email: string, password: string) => {
    setLoading(true)
    try {
      const result = await loginRequest(email, password)
      const current = await getMe(result.access_token)

      localStorage.setItem(TOKEN_KEY, result.access_token)
      setToken(result.access_token)
      setUser(current)
    } finally {
      setLoading(false)
    }
  }, [])

  const value = useMemo(
    () => ({ token, user, loading, login, logout, refreshUser }),
    [token, user, loading, login, logout, refreshUser]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth deve ser usado dentro de AuthProvider.')
  return context
}
