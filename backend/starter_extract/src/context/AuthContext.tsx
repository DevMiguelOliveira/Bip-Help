import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import type { User } from '../types'
import { getMe, login as loginRequest } from '../services/auth'
import { setUnauthorizedHandler } from '../lib/api'

interface AuthContextValue {
  token: string | null
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(false)

  const logout = useCallback(() => {
    setToken(null)
    setUser(null)
  }, [])

  useEffect(() => {
    setUnauthorizedHandler(logout)
  }, [logout])

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
      setToken(result.access_token)
      setUser(current)
    } finally {
      setLoading(false)
    }
  }, [])

  const value = useMemo(() => ({ token, user, loading, login, logout, refreshUser }), [token, user, loading, login, logout, refreshUser])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth deve ser usado dentro de AuthProvider.')
  return context
}
