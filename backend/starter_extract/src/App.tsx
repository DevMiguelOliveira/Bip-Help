import { Navigate, Route, Routes } from 'react-router-dom'
import type { ReactNode } from 'react'
import AppShell from './components/AppShell'
import { ProtectedRoute } from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import TicketsPage from './pages/TicketsPage'
import FranchisesPage from './pages/FranchisesPage'
import UsersPage from './pages/UsersPage'
import SettingsPage from './pages/SettingsPage'
import { useAuth } from './context/AuthContext'

function AdminOnly({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  if (user?.perfil_sistema !== 'administrador') return <Navigate to="/" replace />
  return children
}

export default function App() {
  const { token } = useAuth()
  return <Routes>
    <Route path="/login" element={token ? <Navigate to="/" replace /> : <LoginPage />} />
    <Route element={<ProtectedRoute />}>
      <Route element={<AppShell />}>
        <Route index element={<DashboardPage />} />
        <Route path="tickets" element={<TicketsPage />} />
        <Route path="franchises" element={<FranchisesPage />} />
        <Route path="users" element={<AdminOnly><UsersPage /></AdminOnly>} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
    </Route>
    <Route path="*" element={<Navigate to={token ? '/' : '/login'} replace />} />
  </Routes>
}
