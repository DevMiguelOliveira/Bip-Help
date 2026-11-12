import { useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ArrowRight, CheckCircle2, Clock3, Filter, MessageSquare, Plus, RefreshCw, Ticket, TrendingUp, Building2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getFranchises, getTickets } from '../services/data'
import NewTicketDialog from './NewTicketDialog'
import { formatDate, statusClass } from '../lib/format'

export default function DashboardPage() {
  const { token, user } = useAuth()
  const [filter, setFilter] = useState('all')
  const [showNew, setShowNew] = useState(false)
  const { data: franchises = [], isLoading: loadingFranchises, refetch: refetchFranchises } = useQuery({ queryKey: ['franchises'], queryFn: () => getFranchises(token!), enabled: !!token })
<<<<<<< HEAD
  const { data: tickets = [], isLoading: loadingTickets, refetch } = useQuery({ queryKey: ['tickets'], queryFn: () => getTickets(token!), enabled: !!token, refetchInterval: 10_000, refetchIntervalInBackground: false })
=======
  const { data: tickets = [], isLoading: loadingTickets, refetch } = useQuery({ queryKey: ['tickets'], queryFn: () => getTickets(token!), enabled: !!token })
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806

  const scopedTickets = useMemo(() => tickets.filter((t) => filter === 'all' || String(t.franquia_id) === filter), [tickets, filter])
  const opened = scopedTickets.filter((t) => t.status === 'Aberto').length
  const inProgress = scopedTickets.filter((t) => t.status === 'Em Atendimento').length
  const closed = scopedTickets.filter((t) => t.status === 'Encerrado').length
  const recent = [...scopedTickets].sort((a, b) => new Date(b.criado_em).getTime() - new Date(a.criado_em).getTime()).slice(0, 6)
  const selectedName = filter === 'all' ? 'Todas as unidades' : franchises.find((f) => String(f.id) === filter)?.unidade || 'Unidade selecionada'
  const isLoading = loadingFranchises || loadingTickets

  async function refresh() { await Promise.all([refetch(), refetchFranchises()]) }

  return (
    <div className="page-stack">
      <section className="welcome-row"><div><div className="eyebrow muted-eyebrow"><span className="status-dot" /> CENTRAL DE OPERAÇÕES</div><h1>Bom trabalho, {user?.nome?.split(' ')[0]}.</h1><p>Acompanhe o que acontece nas suas unidades e mantenha o atendimento em movimento.</p></div><div className="welcome-actions"><button className="secondary-button" onClick={refresh}><RefreshCw size={16} /> Atualizar</button><button className="primary-button" onClick={() => setShowNew(true)}><Plus size={17} /> Novo chamado</button></div></section>
      <section className="dashboard-filter-row"><div className="filter-caption"><Filter size={15} /><span>Visão de atendimento</span></div><select className="select-control" value={filter} onChange={(e) => setFilter(e.target.value)}><option value="all">Todas as unidades</option>{franchises.map((f) => <option key={f.id} value={f.id}>{f.unidade}</option>)}</select><span className="filter-context">Exibindo: <strong>{selectedName}</strong></span></section>
      {isLoading ? <div className="panel loading-panel">Carregando indicadores da API…</div> : <>
        <section className="stat-grid">
          <StatCard label="Total de chamados" value={scopedTickets.length} detail="No escopo selecionado" icon={<Ticket size={19} />} tone="blue" trend="Base consolidada" />
          <StatCard label="Abertos" value={opened} detail="Aguardando atendimento" icon={<Clock3 size={19} />} tone="amber" trend="Fila de entrada" />
          <StatCard label="Em atendimento" value={inProgress} detail="Em acompanhamento" icon={<MessageSquare size={19} />} tone="violet" trend="Em andamento" />
          <StatCard label="Encerrados" value={closed} detail="Atendimentos concluídos" icon={<CheckCircle2 size={19} />} tone="green" trend="Concluídos" />
        </section>
        <section className="dashboard-main-grid">
          <div className="panel recent-panel"><div className="panel-heading"><div><span className="section-kicker">ACOMPANHAMENTO</span><h2>Chamados recentes</h2><p>Últimas solicitações registradas nas unidades.</p></div><Link to="/tickets" className="text-link">Ver todos <ArrowRight size={15} /></Link></div>
            {recent.length ? <div className="recent-table-wrap"><table className="data-table"><thead><tr><th>Chamado</th><th>Descrição</th><th>Status</th><th>Abertura</th></tr></thead><tbody>{recent.map((t) => <tr key={t.id}><td><Link to={`/tickets?selected=${t.id}`} className="ticket-code">#{String(t.id).padStart(5, '0')}</Link><small className="table-sub">{franchises.find((f) => f.id === t.franquia_id)?.unidade || `Unidade ${t.franquia_id}`}</small></td><td><span className="description-cell">{t.descricao}</span></td><td><span className={`status-badge ${statusClass(t.status)}`}>{t.status}</span></td><td className="date-cell">{formatDate(t.criado_em)}</td></tr>)}</tbody></table></div> : <EmptyState title="Nenhum chamado por aqui" text="Quando uma solicitação for aberta, ela aparecerá nesta lista." />}
          </div>
          <div className="panel unit-panel"><div className="panel-heading compact-heading"><div><span className="section-kicker">REDE</span><h2>Suas unidades</h2></div><Building2 size={19} className="heading-icon" /></div><div className="unit-list">{franchises.map((f) => { const count = tickets.filter((t) => t.franquia_id === f.id).length; return <div className="unit-item" key={f.id}><div className="unit-avatar">{f.unidade.slice(0, 1).toUpperCase()}</div><div className="unit-info"><strong>{f.unidade}</strong><small>{f.nome_responsavel}</small></div><span className="unit-count">{count} <small>chamados</small></span></div> })}{!franchises.length && <p className="empty-inline">Nenhuma unidade vinculada.</p>}</div><div className="unit-panel-footer"><span><span className="status-dot" /> {franchises.length} unidade(s) no escopo</span></div></div>
        </section>
        <section className="bottom-insight"><div className="insight-icon"><TrendingUp size={18} /></div><div><strong>Visão consolidada do atendimento</strong><span>Os dados exibidos respeitam as permissões da sua conta e as unidades vinculadas no BIPManager.</span></div><span className="insight-tag">DADOS DA API</span></section>
      </>}
      {showNew && <NewTicketDialog franchises={franchises} onClose={() => setShowNew(false)} />}
    </div>
  )
}

function StatCard({ label, value, detail, icon, tone, trend }: { label: string; value: number; detail: string; icon: ReactNode; tone: string; trend: string }) {
  return <div className="stat-card"><div className="stat-top"><span>{label}</span><span className={`stat-icon ${tone}`}>{icon}</span></div><div className="stat-value">{value.toLocaleString('pt-BR')}</div><div className="stat-bottom"><span>{detail}</span><span className="stat-trend">{trend}</span></div></div>
}

function EmptyState({ title, text }: { title: string; text: string }) { return <div className="empty-state"><div className="empty-icon"><Ticket size={22} /></div><strong>{title}</strong><p>{text}</p></div> }
