import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { LogOut, Shield, Users, Settings, Router, Dumbbell, PieChart, BarChart2, Clipboard, Calendar, Lock, AlertCircle, Folder, Mail, Award, Timer, Users2, FolderSearch, Layout, MailCheck, TrendingUp, MessageCircle, Home, LogOut as LogOutSolid } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function AdminPage() {
  const { user, token } = useAuth()
  const [section, setSection] = useState<'dashboard' | 'users' | 'bip-bot' | 'notifications' | 'security' | 'settings'>('dashboard')
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  // Dashboard stats
  const [stats, setStats] = useState({
    totalUsers: 0,
    activeSessions: 0,
    newTickets: 0,
    openChats: 0
  })

  useEffect(() => {
    // Buscar estatísticas do admin
    fetch('/api/admin/stats', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(setStats)
      .catch(() => setStats({ totalUsers: 0, activeSessions: 0, newTickets: 0, openChats: 0 }))
  }, [token])

  const sections = [
    { key: 'dashboard', title: 'Visão Geral', icon: Layout, href: '/admin' },
    { key: 'users', title: 'Usuários', icon: Users, href: '/admin/users' },
    { key: 'bip-bot', title: 'BIP Bot', icon: Dumbbell, href: '/admin/bip-bot' },
    { key: 'notifications', title: 'Notificações', icon: AlertCircle, href: '/admin/notifications' },
    { key: 'security', title: 'Segurança', icon: Lock, href: '/admin/security' },
    { key: 'settings', title: 'Configurações', icon: Settings, href: '/admin/settings' }
  ]

  function toggleSidebar() {
    setSidebarCollapsed(!sidebarCollapsed)
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-gray-800 flex-shrink-0 sidebar collapsed:shrink-0 transition-colors" onClick={e => e.stopPropagation()}>
        <div className="h-14 border-b border-gray-700 px-4 flex items-center justify-between">
          <h2 className="font-bold text-xl text-white">BIPManager Admin</h2>
          <button onClick={toggleSidebar} className="p-2 text-gray-400 hover:text-white">
            {sidebarCollapsed ? <Layout size={24} /> : <ArrowRight size={24} />}
          </button>
        </div>
        <ul className="space-y-1 px-2 py-2 max-h-[calc(100vh-140px)] overflow-y-auto">
          {sections.map((s) => (
            <li key={s.key} className={sidebarCollapsed
              ? "hover:bg-gray-700 text-sm px-2 rounded-md"
              : "flex items-center gap-3 px-2 py-2 rounded-md hover:bg-gray-700 font-medium transition-colors"}
            >
              <Link
                href={s.href}
                className={sidebarCollapsed
                  ? "block text-gray-300"
                  : "items-center gap-2 text-white"}
              >
                <s.icon className="w-4 h-4" />
                <span>{s.title}</span>
              </Link>
            </li>
          ))}
          <li>
            <button onClick={toggleSidebar} className="w-full text-left p-2 text-sm text-gray-400 hover:bg-gray-700">
              Expandir sidebar
            </button>
          </li>
        </ul>
      </div>

      {/* Content Area */}
      <div className="flex-1 p-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Painel Administrativo</h1>
          <button onClick={toggleSidebar} className="sm:hidden p-2 text-gray-400 hover:text-white">
            <LogOutSolid size={20} />
          </button>
        </div>

        {/* Current Section Content */}
        <div className="bg-white rounded-xl shadow-sm p-6 min-h-[400px]">
          {/* Dashboard Section */}
          {section === 'dashboard' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">Visão Geral do Sistema</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-200">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center">
                      <Users2 className="text-blue-600 text-lg" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-600">{stats.totalUsers} Usuários</p>
                      <p className="text-sm text-gray-400">Total de usuários cadastrados</p>
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-200">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-green-100 flex items-center justify-center">
                      <Award className="text-green-600 text-lg" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-600">{stats.activeSessions} Sessões Ativas</p>
                      <p className="text-sm text-gray-400">Sessões ativas atualmente</p>
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-200">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-yellow-100 flex items-center justify-center">
                      <Timer className="text-yellow-600 text-lg" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-600">{stats.newTickets} Novos Chamados</p>
                      <p className="text-sm text-gray-400">Novos chamados hoje</p>
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-200">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-red-100 flex items-center justify-center">
                      <MessageCircle className="text-red-600 text-lg" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-600">{stats.openChats} Chats Abertos</p>
                      <p className="text-sm text-gray-400">Chats ativos simultâneos</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Users Section */}
          {section === 'users' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">Gestão de Usuários</h2>
              <p className="text-gray-500 mb-4">
                Administre usuários e permissões do sistema
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-200">
                  <h3 className="font-medium text-gray-600">Perfis de Acesso</h3>
                  <ul className="list-disc list-inside text-gray-500 space-y-1">
                    <li>Administrador - Acesso total ao sistema</li>
                    <li>Suporte N1 - Atendimento de primeiro nível</li>
                    <li>Suporte N2 - Atendimento de segundo nível</li>
                    <li>Operador - Acesso restrito a funcionalidades</li>
                  </ul>
                </div>
                <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-200">
                  <h3 className="font-medium text-gray-600">Unidades Vinculadas</h3>
                  <p className="text-gray-400 text-sm">
                    <span className="font-bold">0</span> unidades vinculadas (neste exemplo)
                  </p>
                </div>
              </div>
              <p className="text-gray-500 mt-4">
                Clique em um perfil acima para mais detalhes
              </p>
            </div>
          )}

          {/* BIP Bot Section */}
          {section === 'bip-bot' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">BIP Bot</h2>
              <p className="text-gray-500 mb-4">
                Roteiro de perguntas, mensagens e regras de triagem
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-200">
                  <h3 className="font-medium text-gray-600">Fluxo Guiado</h3>
                  <ul className="list-disc list-inside text-gray-500 space-y-1">
                    <li>Menu de opções iniciais</li>
                    <li>Perguntas de qualificação</li>
                    <li>Ramificações por problema</li>
                    <li>Respostas automáticas</li>
                  </ul>
                </div>
                <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-200">
                  <h3 className="font-medium text-gray-600">Configuração</h3>
                  <ul className="list-disc list-inside text-gray-500 space-y-1">
                    <li>Capacidade padrão: 10 chamados</li>
                    <li>Distribuição por equipe</li>
                    <li>Balanceamento de carga</li>
                    <li>Fila de espera</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Notifications Section */}
          {section === 'notifications' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">Notificações</h2>
              <p className="text-gray-500 mb-4">
                Alertas de novos chamados, transferências e fila de espera
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-200">
                  <h3 className="font-medium text-gray-600">Alertas de Novos Chamados</h3>
                  <p className="text-gray-400 text-sm">
                    <span className="font-bold">Ativado</span> - Receberá notificação sempre que um novo chamado for criado
                  </p>
                </div>
                <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-200">
                  <h3 className="font-medium text-gray-600">Transferências</h3>
                  <p className="text-gray-400 text-sm">
                    <span className="font-bold">Desativado</span> - Notificações de transferência entre equipes
                  </p>
                </div>
                <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-200">
                  <h3 className="font-medium text-gray-600">Fila de Espera</h3>
                  <p className="text-gray-400 text-sm">
                    <span className="font-bold">Ativado</span> - Alertas quando chamados aguardam atendimento
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Security Section */}
          {section === 'security' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">Segurança</h2>
              <p className="text-gray-500 mb-4">
                Permissões, sessões e histórico das ações administrativas
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-200">
                  <h3 className="font-medium text-gray-600">Autenticação</h3>
                  <p className="text-gray-400 text-sm">
                    <span className="font-bold">JWT Token</span> - Token JWT mantido em memória nesta versão
                  </p>
                  <p className="text-gray-400 text-xs">
                    Ao recarregar, será necessário entrar novamente
                  </p>
                </div>
                <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-200">
                  <h3 className="font-medium text-gray-600">Sessões Ativas</h3>
                  <p className="text-gray-400 text-sm">
                    Sessão atual: Administrador (luismiguelipg2018@gmail.com)
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Settings Section */}
          {section === 'settings' && (
            <div>
              <h2 className="text-xl font-semibold text-gray-700 mb-4">Configurações Administrativas</h2>
              <p className="text-gray-500 mb-4">
                Áreas previstas para administrar a operação do BIPManager
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-200">
                  <h3 className="font-medium text-gray-600">Identidade Visual</h3>
                  <p className="text-gray-400 text-sm">
                    Cores primárias, secundárias e parâmetros de branding da plataforma
                  </p>
                </div>
                <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-200">
                  <h3 className="font-medium text-gray-600">Preferências do Sistema</h3>
                  <p className="text-gray-400 text-sm">
                    Configurações gerais da plataforma, horários de funcionamento, etc.
                  </p>
                </div>
                <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-200">
                  <h3 className="font-medium text-gray-600">Canais Internos</h3>
                  <p className="text-gray-400 text-sm">
                    Organização do Suporte N1/N2 e disponibilidade da equipe
                  </p>
                </div>
                <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-200">
                  <h3 className="font-medium text-gray-600">Controle de Acesso</h3>
                  <p className="text-gray-400 text-sm">
                    Permissões, sessões e histórico das ações administrativas
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}