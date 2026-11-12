import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import {
  Bell, Bot, Building2, BarChart3, ChevronDown,
  Headset, Inbox, LayoutDashboard, LogOut, Menu, PanelLeftClose, PanelLeftOpen,
  Settings2, ShieldCheck, Store, Ticket, UserRound, Users,
} from 'lucide-react'
import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { ThemeToggle } from './ThemeToggle'

type NavItem = { to: string; label: string; icon: typeof LayoutDashboard; end?: boolean; badge?: string }

const staffPages: Record<string, string> = {
  '/': 'Visão geral', '/tickets': 'Central de chamados', '/bot': 'BIP Bot',
  '/queue': 'Fila de espera', '/team': 'Equipe de suporte',
  '/performance': 'Desempenho', '/franchises': 'Franquias',
  '/users': 'Gestão de usuários', '/settings': 'Configurações',
}
const clientPages: Record<string, string> = {
  '/': 'Início', '/tickets': 'Meus chamados', '/settings': 'Minha conta',
}

export default function AppShell() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [theme, setTheme] = useState<'light' | 'dark'>(() => (localStorage.getItem('bip-theme') as 'light' | 'dark') || 'light')
  const [collapsed, setCollapsed] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const isAdmin = user?.perfil_sistema === 'administrador'
  const isSupport = user?.perfil_sistema === 'suporte_n1' || user?.perfil_sistema === 'suporte_n2'
  const isInternal = isAdmin || isSupport

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('bip-theme', theme)
  }, [theme])

  useEffect(() => {
    setMobileMenuOpen(false)
  }, [location.pathname])

  const signOut = () => { logout(); navigate('/login', { replace: true }) }
  const title = (isInternal ? staffPages : clientPages)[location.pathname] || 'BIPManager'
  const staffPrimary: NavItem[] = [
    { to: '/', label: 'Visão geral', icon: LayoutDashboard, end: true },
    { to: '/tickets', label: 'Chamados', icon: Ticket, badge: 'Live' },
    { to: '/bot', label: 'BIP Bot', icon: Bot },
    { to: '/queue', label: 'Fila de espera', icon: Inbox },
    { to: '/team', label: 'Equipe N1/N2', icon: Users },
    { to: '/performance', label: 'Desempenho', icon: BarChart3 },
  ]
  const clientPrimary: NavItem[] = [
    { to: '/', label: 'Início', icon: LayoutDashboard, end: true },
    { to: '/tickets', label: 'Meus chamados', icon: Ticket },
  ]
  const primary = isInternal ? staffPrimary : clientPrimary

  return (
    <div className={`app-shell ${collapsed ? 'sidebar-collapsed' : ''} ${isInternal ? 'staff-shell' : 'client-shell'}`}>
      {mobileMenuOpen && <button type="button" className="sidebar-overlay" aria-label="Fechar menu" onClick={() => setMobileMenuOpen(false)} />}
      <aside className={`sidebar ${mobileMenuOpen ? 'mobile-open' : ''}`}>
        <div className="brand-lockup">
          <div className="brand-mark"><span>B</span><i /></div>
          {!collapsed && <div className="brand-copy"><strong>BIPManager</strong><small>{isInternal ? 'SUPPORT PLATFORM' : 'PORTAL DA FRANQUIA'}</small></div>}
        </div>
        <div className="workspace-chip">
          <div className="workspace-symbol">{isInternal ? <Headset size={17} /> : <Store size={17} />}</div>
          {!collapsed && <><div className="workspace-copy"><strong>{isInternal ? 'Central de Suporte' : 'Área da Franquia'}</strong><small>{isInternal ? (isAdmin ? 'Administração' : 'Operação de suporte') : 'Portal de atendimento'}</small></div><ChevronDown size={14} /></>}
        </div>
        <div className="nav-section-label">{isInternal ? 'OPERAÇÃO' : 'ATENDIMENTO'}</div>
        <nav className="main-nav">
          {primary.map((item) => {
            const Icon = item.icon
            return <NavLink key={item.to} to={item.to} end={item.end} title={item.label} onClick={() => setMobileMenuOpen(false)}><Icon size={18} /><span>{item.label}</span>{item.badge && <span className="nav-pill">{item.badge}</span>}</NavLink>
          })}
          {isInternal && <>
            {(isAdmin || isSupport) && <NavLink to="/franchises" title="Franquias" onClick={() => setMobileMenuOpen(false)}><Building2 size={18} /><span>Franquias</span></NavLink>}
            {isAdmin && <NavLink to="/users" title="Usuários" onClick={() => setMobileMenuOpen(false)}><UserRound size={18} /><span>Usuários</span></NavLink>}
          </>}
        </nav>
        <div className="nav-section-label secondary-label">{isInternal ? 'ADMINISTRAÇÃO' : 'CONTA'}</div>
        <nav className="main-nav">
          <NavLink to="/settings" title={isInternal ? 'Configurações' : 'Minha conta'} onClick={() => setMobileMenuOpen(false)}><Settings2 size={18} /><span>{isInternal ? 'Configurações' : 'Minha conta'}</span></NavLink>
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
        <div className="sidebar-footer">{!collapsed && 'BIPMANAGER • 0.2.0'}</div>
      </aside>
      <main className="main-area">
        <header className="topbar">
          <button type="button" className="mobile-menu-button" aria-label="Abrir menu" aria-expanded={mobileMenuOpen} onClick={() => setMobileMenuOpen((v) => !v)}><Menu size={21} /></button>
          <div className="breadcrumb"><span>{isInternal ? 'Suporte' : 'Portal'}</span><span className="crumb-slash">/</span><strong>{title}</strong></div>
          <div className="topbar-actions">
            {isInternal && <div className="system-status"><span className="status-dot" /> Operação normal</div>}
            <button className="icon-button notification-button" aria-label="Notificações" title="Notificações"><Bell size={18} /><i /></button>
            <ThemeToggle theme={theme} onToggle={() => setTheme((value) => value === 'light' ? 'dark' : 'light')} />
            <div className="topbar-divider" />
            <button className="profile-menu" onClick={signOut} title="Sair da conta">
              <div className="avatar">{user?.nome?.trim().split(/\s+/).slice(0, 2).map((x) => x[0]).join('').toUpperCase()}</div>
              <div className="profile-copy"><strong>{user?.nome}</strong><small>{isAdmin ? 'Administrador' : isSupport ? (user?.perfil_sistema === 'suporte_n2' ? 'Suporte N2' : 'Suporte N1') : 'Franqueado'}</small></div>
              <LogOut size={16} className="logout-icon" />
            </button>
          </div>
        </header>
        <div className="page-container"><Outlet /></div>
      </main>
    </div>
  )
}
