import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Filter, Plus, Search, Ticket as TicketIcon, RefreshCw, MessageCircle, CalendarDays } from 'lucide-react'
import { useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getFranchises, getTickets } from '../services/data'
import NewTicketDialog from './NewTicketDialog'
import TicketChatDialog from './TicketChatDialog'
import { formatDate, statusClass } from '../lib/format'

export default function TicketsPage() {
  const { token } = useAuth()
  const [params, setParams] = useSearchParams()
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('all')
  const [franchise, setFranchise] = useState('all')
  const [showNew, setShowNew] = useState(false)
  const { data: franchises = [] } = useQuery({ queryKey: ['franchises'], queryFn: () => getFranchises(token!), enabled: !!token })
  const { data: tickets = [], isLoading, isError, error, refetch } = useQuery({ queryKey: ['tickets'], queryFn: () => getTickets(token!), enabled: !!token, refetchInterval: 10_000, refetchIntervalInBackground: false })
  const filtered = useMemo(() => tickets.filter((ticket) => {
    const matchesSearch = !search || String(ticket.id).includes(search) || ticket.descricao.toLowerCase().includes(search.toLowerCase())
    const matchesStatus = status === 'all' || ticket.status === status
    const matchesFranchise = franchise === 'all' || String(ticket.franquia_id) === franchise
    return matchesSearch && matchesStatus && matchesFranchise
  }).sort((a, b) => new Date(b.criado_em).getTime() - new Date(a.criado_em).getTime()), [tickets, search, status, franchise])
  const selectedId = Number(params.get('selected')) || null
  const selectedTicket = selectedId ? tickets.find((t) => t.id === selectedId) : undefined
  const openTicket = (id: number) => setParams({ selected: String(id) })
  const closeTicket = () => setParams({})

  return <div className="page-stack"><section className="welcome-row"><div><div className="eyebrow muted-eyebrow">CENTRAL DE ATENDIMENTO</div><h1>Chamados</h1><p>Acompanhe solicitações, atualizações e conversas das unidades.</p></div><div className="welcome-actions"><button className="secondary-button" onClick={() => refetch()}><RefreshCw size={16} /> Atualizar</button><button className="primary-button" onClick={() => setShowNew(true)}><Plus size={17} /> Novo chamado</button></div></section>
    <section className="ticket-summary-row"><div className="mini-stat"><span className="mini-stat-icon blue"><TicketIcon size={17} /></span><div><strong>{tickets.length}</strong><small>Total de chamados</small></div></div><div className="mini-stat"><span className="mini-stat-icon amber"><CalendarDays size={17} /></span><div><strong>{tickets.filter((t) => t.status === 'Aberto').length}</strong><small>Abertos</small></div></div><div className="mini-stat"><span className="mini-stat-icon violet"><MessageCircle size={17} /></span><div><strong>{tickets.filter((t) => t.status === 'Em Atendimento').length}</strong><small>Em atendimento</small></div></div><div className="mini-stat"><span className="mini-stat-icon green"><TicketIcon size={17} /></span><div><strong>{tickets.filter((t) => t.status === 'Encerrado').length}</strong><small>Encerrados</small></div></div></section>
    <section className="panel tickets-panel"><div className="panel-heading tickets-heading"><div><span className="section-kicker">SOLICITAÇÕES</span><h2>Todos os chamados</h2><p>{filtered.length} resultado(s) na visualização atual.</p></div></div><div className="table-toolbar"><div className="search-field"><Search size={17} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar por número ou descrição…" /></div><div className="toolbar-filters"><select className="select-control" value={franchise} onChange={(e) => setFranchise(e.target.value)}><option value="all">Todas as unidades</option>{franchises.map((f) => <option key={f.id} value={f.id}>{f.unidade}</option>)}</select><select className="select-control" value={status} onChange={(e) => setStatus(e.target.value)}><option value="all">Todos os status</option><option>Aberto</option><option>Em Atendimento</option><option>Encerrado</option></select></div></div>
      {isLoading ? <div className="loading-panel">Carregando chamados…</div> : isError ? <div className="error-panel">{(error as Error).message}</div> : filtered.length ? <div className="recent-table-wrap"><table className="data-table tickets-data-table"><thead><tr><th>Identificação</th><th>Descrição</th><th>Unidade</th><th>Status</th><th>Data</th><th /></tr></thead><tbody>{filtered.map((t) => <tr key={t.id} onClick={() => openTicket(t.id)} className="clickable-row"><td><span className="ticket-code">#{String(t.id).padStart(5, '0')}</span></td><td><span className="description-cell">{t.descricao}</span></td><td>{franchises.find((f) => f.id === t.franquia_id)?.unidade || `Unidade ${t.franquia_id}`}</td><td><span className={`status-badge ${statusClass(t.status)}`}>{t.status}</span></td><td className="date-cell">{formatDate(t.criado_em)}</td><td><button className="table-action" aria-label="Abrir conversa"><MessageCircle size={16} /></button></td></tr>)}</tbody></table></div> : <div className="empty-state"><div className="empty-icon"><Filter size={22} /></div><strong>Nenhum chamado encontrado</strong><p>Altere os filtros ou abra uma nova solicitação.</p></div>}
    </section>
    {showNew && <NewTicketDialog franchises={franchises} onClose={() => setShowNew(false)} />}
    {selectedTicket && <TicketChatDialog ticket={selectedTicket} onClose={closeTicket} />}
  </div>
}
