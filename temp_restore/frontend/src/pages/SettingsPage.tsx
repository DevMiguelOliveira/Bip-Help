import { Bell, Bot, CircleHelp, Gauge, GitBranch, ShieldCheck, SlidersHorizontal, Tags, UserCircle2, Users } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const adminSettings = [
  { icon: Bot, title: 'BIP Bot', description: 'Roteiro de perguntas, mensagens e regras de triagem.', detail: 'Configuração do fluxo guiado' },
  { icon: Users, title: 'Equipes e atendentes', description: 'Organização do Suporte N1/N2 e disponibilidade da equipe.', detail: 'Capacidade padrão: 10 chamados' },
  { icon: GitBranch, title: 'Distribuição de chamados', description: 'Balanceamento de carga, fila de espera e transferências.', detail: 'Balanceamento inteligente' },
  { icon: Tags, title: 'Categorias', description: 'Tipos de solicitação e classificação dos chamados.', detail: 'Categorias operacionais' },
  { icon: Gauge, title: 'Prioridades e SLA', description: 'Prazos de resposta, resolução e escalonamento.', detail: 'Regras ainda não conectadas' },
  { icon: Bell, title: 'Notificações', description: 'Alertas de novos chamados, transferências e fila de espera.', detail: 'Canais internos do BIPManager' },
  { icon: ShieldCheck, title: 'Segurança e auditoria', description: 'Permissões, sessões e histórico das ações administrativas.', detail: 'Controle de acesso' },
  { icon: SlidersHorizontal, title: 'Preferências gerais', description: 'Identidade visual e parâmetros gerais da plataforma.', detail: 'Preferências do sistema' },
]

export default function SettingsPage() {
  const { user } = useAuth()
  const isAdmin = user?.perfil_sistema === 'administrador'
  const isSupport = user?.perfil_sistema === 'suporte_n1'
  return <div className="page-stack">
    <section className="welcome-row"><div><div className="eyebrow muted-eyebrow">{isAdmin ? 'ADMINISTRAÇÃO' : 'PREFERÊNCIAS'}</div><h1>{isAdmin ? 'Configurações' : 'Minha conta'}</h1><p>{isAdmin ? 'Gerencie os parâmetros da operação de suporte.' : 'Consulte as informações da sua conta e sessão.'}</p></div></section>
    <section className="settings-grid">
      <article className="panel settings-card"><div className="settings-card-icon"><UserCircle2 size={21}/></div><div><span className="section-kicker">CONTA</span><h2>Perfil de acesso</h2><p>Informações obtidas da sessão autenticada.</p></div><div className="settings-detail"><span>Nome</span><strong>{user?.nome}</strong></div><div className="settings-detail"><span>E-mail</span><strong>{user?.email}</strong></div><div className="settings-detail"><span>Perfil de sistema</span><strong>{isAdmin ? 'Administrador' : isSupport ? 'Suporte' : 'Usuário de franquia'}</strong></div><div className="settings-detail"><span>Unidades vinculadas</span><strong>{user?.franquias?.length || 0}</strong></div></article>
      <article className="panel settings-card"><div className="settings-card-icon"><ShieldCheck size={21}/></div><div><span className="section-kicker">SEGURANÇA</span><h2>Sessão autenticada</h2><p>O acesso utiliza token JWT mantido em memória nesta versão.</p></div><div className="security-detail"><span className="status-dot"/> Autenticação ativa</div><div className="security-detail"><ShieldCheck size={16}/> API protegida por autenticação</div><div className="security-detail"><CircleHelp size={16}/> Ao recarregar, será necessário entrar novamente</div></article>
    </section>
    {isAdmin && <section className="settings-admin-section"><div className="panel-heading"><div><span className="section-kicker">CONTROLE DA PLATAFORMA</span><h2>Configurações administrativas</h2><p>Áreas previstas para administrar a operação do BIPManager.</p></div></div><div className="settings-admin-grid">{adminSettings.map((item) => { const Icon = item.icon; return <article className="panel settings-admin-card" key={item.title}><div className="settings-admin-icon"><Icon size={19}/></div><div className="settings-admin-copy"><strong>{item.title}</strong><span>{item.description}</span><small>{item.detail}</small></div></article> })}</div><div className="workspace-notice"><ShieldCheck size={18}/><div><strong>Configurações em construção</strong><span>Esta entrega organiza a interface. Os formulários e controles serão ativados quando suas respectivas APIs forem implementadas e protegidas no backend.</span></div></div></section>}
  </div>
}
