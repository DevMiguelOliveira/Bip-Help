import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { Bell, ChevronDown, LayoutDashboard, LogOut, Settings2, ShieldCheck, Ticket, Users, Store, PanelLeftClose, PanelLeftOpen, Headset } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { ThemeToggle } from './ThemeToggle'

const pageNames: Record<string, string> = {
  '/': 'Visão geral', '/tickets': 'Central de chamados', '/franchises': 'Franquias', '/users': 'Gestão de usuários', '/settings': 'Configurações',
}

export default function AppShell() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [theme, setTheme] = useState<'light' | 'dark'>(() => (localStorage.getItem('bip-theme') as 'light' | 'dark') || 'light')
  const [collapsed, setCollapsed] = useState(false)
  const isAdmin = user?.perfil_sistema === 'administrador'
  const isSupport = user?.perfil_sistema === 'suporte_n1'

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('bip-theme', theme)
  }, [theme])

  const toggleTheme = () => setTheme((value) => value === 'light' ? 'dark' : 'light')
  const signOut = () => { logout(); navigate('/login', { replace: true }) }
  const title = pageNames[location.pathname] || 'BIPManager'

  return (
    <div className={`app-shell ${collapsed ? 'sidebar-collapsed' : ''}`}>
      <aside className="sidebar">
        <div className="brand-lockup">
          <div className="brand-mark"><span>B</span><i /></div>
          {!collapsed && <div className="brand-copy"><strong>BIPManager</strong><small>SUPPORT PLATFORM</small></div>}
        </div>
        <div className="workspace-chip">
          <div className="workspace-symbol"><Headset size={17} /></div>
          {!collapsed && <><div className="workspace-copy"><strong>Central BIP360</strong><small>Ambiente de suporte</small></div><ChevronDown size={14} /></>}
        </div>
        <div className="nav-section-label">WORKSPACE</div>
        <nav className="main-nav">
          <NavLink to="/" end title="Visão geral"><LayoutDashboard size={18} /><span>Visão geral</span></NavLink>
          <NavLink to="/tickets" title="Chamados"><Ticket size={18} /><span>Chamados</span><span className="nav-pill">Live</span></NavLink>
          {(isAdmin || isSupport) && <NavLink to="/franchises" title="Franquias"><Store size={18} /><span>Franquias</span></NavLink>}
          {isAdmin && <NavLink to="/users" title="Usuários"><Users size={18} /><span>Usuários</span></NavLink>}
        </nav>
        <div className="nav-section-label secondary-label">PREFERÊNCIAS</div>
        <nav className="main-nav">
          <NavLink to="/settings" title="Configurações"><Settings2 size={18} /><span>Configurações</span></NavLink>
        </nav>
        <div className="sidebar-spacer" />
        <div className="security-note">
          <div className="security-icon"><ShieldCheck size={17} /></div>
          {!collapsed && <div><strong>Ambiente protegido</strong><small>Sessão autenticada</small></div>}
        </div>
        <button className="collapse-button" onClick={() => setCollapsed((v) => !v)}>
          {collapsed ? <PanelLeftOpen size={17} /> : <PanelLeftClose size={17} />}
          {!collapsed && <span>Recolher menu</span>}
        </button>
        <div className="sidebar-footer">{!collapsed && 'BIPMANAGER • 0.1.0'}</div>
      </aside>
      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb"><span>Workspace</span><span className="crumb-slash">/</span><strong>{title}</strong></div>
          <div className="topbar-actions">
            <div className="system-status"><span className="status-dot" /> Operação normal</div>
            <button className="icon-button notification-button" aria-label="Notificações"><Bell size={18} /><i /></button>
            <ThemeToggle theme={theme} onToggle={toggleTheme} />
            <div className="topbar-divider" />
            <button className="profile-menu" onClick={signOut} title="Sair da conta">
              <div className="avatar">{user?.nome?.trim().split(/\s+/).slice(0, 2).map((x) => x[0]).join('').toUpperCase()}</div>
              <div className="profile-copy"><strong>{user?.nome}</strong><small>{user?.perfil_sistema || 'Acesso por franquia'}</small></div>
              <LogOut size={16} className="logout-icon" />
            </button>
          </div>
        </header>
        <div className="page-container"><Outlet /></div>
      </main>
    </div>
  )
}
