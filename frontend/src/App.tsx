import { Navigate, Route, Routes } from 'react-router-dom'
import type { ReactNode } from 'react'
import AppShell from './components/AppShell'
import { ProtectedRoute } from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import TicketsPage from './pages/TicketsPage'
import AdminPage from './pages/AdminPage'
import ClientPortalPage from './pages/ClientPortalPage'
import ClientTicketsPage from './pages/ClientTicketsPage'
import FranchisesPage from './pages/FranchisesPage'
import UsersPage from './pages/UsersPage'
import SettingsPage from './pages/SettingsPage'
import BotPage from './pages/BotPage'
import QueuePage from './pages/QueuePage'
import TeamPage from './pages/TeamPage'
import PerformancePage from './pages/PerformancePage'
import { useAuth } from './context/AuthContext'
import './workspace.css'

function isInternalProfile(profile: string | null | undefined) {
  return profile === 'administrador' || profile === 'suporte_n1' || profile === 'suporte_n2'
}

function RoleHome() {
  const { user } = useAuth()
  return isInternalProfile(user?.perfil_sistema) ? <DashboardPage /> : <ClientPortalPage />
}

function InternalOnly({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  if (!isInternalProfile(user?.perfil_sistema)) return <Navigate to="/" replace />
  return children
}

function AdminOnly({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  if (user?.perfil_sistema !== 'administrador') return <Navigate to="/" replace />
  return children
}

export default function App() {
  const { token, user } = useAuth()
  const isInternal = isInternalProfile(user?.perfil_sistema)

  return <Routes>
    <Route path="/login" element={token ? <Navigate to "/" replace /> : <LoginPage />} />
    <Route element={<ProtectedRoute />}>
      <Route element={<AppShell />}>
        <Route index element={<RoleHome />} />
        <Route path="tickets" element={isInternal ? <TicketsPage /> : <ClientTicketsPage />} />
        <Route path="admin" element={AdminPage} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="bot" element={<InternalOnly><BotPage /></InternalOnly>} />
        <Route path="queue" element={<InternalOnly><QueuePage /></InternalOnly>} />
        <Route path="team" element={<InternalOnly><TeamPage /></InternalOnly>} />
        <Route path="performance" element={<InternalOnly><PerformancePage /></InternalOnly>} />
        <Route path="franchises" element={<InternalOnly><FranchisesPage /></InternalOnly>} />
        <Route path="users" element={<AdminOnly><UsersPage /></AdminOnly>} />
      </Route>
    </Route>
    <Route path="*" element={<Navigate to={token ? '/' : '/login'} replace />} />
  </Routes>
}
