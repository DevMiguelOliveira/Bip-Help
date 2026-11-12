import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { LoaderCircle } from 'lucide-react'

export function ProtectedRoute() {
  const { token, user, loading } = useAuth()

  if (loading) return <LoadingScreen />

  if (!token || !user) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}

export function LoadingScreen() {
  return (
    <div className="loading-screen">
      <div className="loading-brand">
        <span className="brand-mark">B</span>
        <span>BIPManager</span>
      </div>
      <LoaderCircle className="spin" size={24} />
    </div>
  )
}
