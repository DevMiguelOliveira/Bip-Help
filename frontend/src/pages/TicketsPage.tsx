import { useMemo, useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Filter, Plus, Search, Ticket as TicketIcon, RefreshCw, MessageCircle } from 'lucide-react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getFranchises, getTickets } from '../services/data'
import NewTicketDialog from './NewTicketDialog'
import { formatDate, statusClass } from '../lib/format'

export default function TicketsPage() {
  const { token } = useAuth()
  const [params, setParams] = useSearchParams()
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('all')
  const [franchise, setFranchise] = useState('all')
  const [showNew, setShowNew] = useState(false)
  const [showFilters, setShowFilters] = useState(false)
  const { data: franchises = [] } = useQuery({ queryKey: ['franchises'], queryFn: () => getFranchises(token!), enabled: !!token })
  const { data: tickets = [], isLoading, isError, error, refetch } = useQuery({ queryKey: ['tickets'], queryFn: () => getTickets(token!, undefined, status, { skip: 0, limit: 50 }), enabled: !!token, refetchInterval: 15_000, refetchIntervalInBackground: false })
  const [unreadCount, setUnreadCount] = useState(0)

  useEffect(() => {
    // Contador de tickets não lidos
    const count = tickets.filter((t) => t.status === 'Aberto' && !t.enviado_para_cliente).length
    setUnreadCount(count)
  }, [tickets])

  const filtered = useMemo(() => tickets.filter((ticket) => {
    const matchesSearch = !search || String(ticket.id).includes(search) || ticket.descricao.toLowerCase().includes(search.toLowerCase())
    const matchesStatus = status === 'all' || ticket.status === status
    const matchesFranchise = franchise === 'all' || String(ticket.franquia_id) === franchise
    return matchesSearch && matchesStatus && matchesFranchise
  }).sort((a, b) => new Date(b.criado_em).getTime() - new Date(a.criado_em).getTime()), [tickets, search, status, franchise])

  const selectedId = Number(params.get('selected')) || null
  const selectedTicket = selectedId ? tickets.find((t) => t.id === selectedId) : undefined
  const navigate = useNavigate()

  const openTicket = (id: number) => setParams({ selected: String(id) })
  const closeTicket = () => setParams({})

  const viewTicket = (id: number) => {
    setParams({ selected: String(id) })
  }

  const statusClassMap: Record<string, string> = {
    Aberto: 'status-badge-active',
    'Em Atendimento': 'status-badge-in-progress',
    Encerrado: 'status-badge-concluded',
  }

  return (
    <section className="tickets-page">
      <header className="page-header">
        <div className="page-header-left">
          <h1>Todas as solicitações</h1>
          <p>{tickets.length} resultado(s) na visualização atual.</p>
        </div>
        <div className="page-header-right">
          <button className="secondary-button" onClick={() => setShowNew(true)}><Plus size={16} /> Novo chamado</button>
          <button className="secondary-button" onClick={() => setShowFilters(true)}><Filter size={16} /> Filtros</button>
        </div>
      </header>

      {/* Resumo rápido */}
      <section className="ticket-summary-row">
        {isLoading ? (
          <div className="skeleton-grid">
            <div className="skeleton-card" width={80} /><div className="skeleton-card" width={60} /><div className="skeleton-card" width={100} />
            <div className="skeleton-card" width={40} /><div className="skeleton-card" width={60} /><div className="skeleton-card" width={80} />
            <div className="skeleton-card" width={40} /><div className="skeleton-card" width={60} /><div className="skeleton-card" width={80} />
          </div>
        ) : (
          <>
            <div className="mini-stat"><span className="mini-stat-icon blue"><TicketIcon size={17} /></span><div><strong>{tickets.length}</strong><small>Total</small></div></div>
            <div className="mini-stat"><span className="mini-stat-icon amber"><Loader2 size={17} /></span><div><strong>{tickets.filter((t) => t.status === 'Aberto').length}</strong><small>Abertos</small></div></div>
            <div className="mini-stat"><span className="mini-stat-icon violet"><MessageCircle size={17} /></span><div><strong>{tickets.filter((t) => t.status === 'Em Atendimento').length}</strong><small>Em atendimento</small></div></div>
            <div className="mini-stat"><span className="mini-stat-icon green"><TicketIcon size={17} /></span><div><strong>{tickets.filter((t) => t.status === 'Encerrado').length}</strong><small>Encerrados</small></div></div>
            <div className="mini-stat"><span className="mini-stat-icon red"><AlertCircle size={17} /></span><div><strong>{unreadCount}</strong><small>Não lidos</small></div></div>
          </>
        )}
      </section>

      {/* Painel de filtros */}
      {showFilters && (
        <section className="panel filters-panel">
          <div className="panel-heading"><div><span className="section-kicker">FILTROS</span><button className="collapse-button" onClick={() => setShowFilters(false)}>&times;</button></div></div>
          <div className="panel-body">
            <div className="filter-group">
              <span>Status</span>
              <select className="select-control" value={status} onChange={(e) => setStatus(e.target.value)}><option value="all">Todos</option><option>Aberto</option><option>Em Atendimento</option><option>Encerrado</option></select>
            </div>
            <div className="filter-group">
              <span>Unidade</span>
              <select className="select-control" value={franchise} onChange={(e) => setFranchise(e.target.value)}><option value="all">Todas</option>{franchises.map((f) => <option key={f.id} value={f.id}>{f.unidade}</option>)}</select>
            </div>
            <div className="filter-group">
              <span>Busca</span>
              <div className="search-field"><Search size={17} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar por número ou descrição..." /></div>
            </div>
          </div>
        </section>
      )}

      {/* Tabela de tickets */}
      <section className="panel tickets-panel">
        <div className="panel-heading tickets-heading">
          <div>
            <span className="section-kicker">SOLICITAÇÕES</span>
            <h2>Todos os chamados</h2>
            <p>{filtered.length} resultado(s) na visualização atual.</p>
          </div>
        </div>

        {isLoading ? (
          <div className="recent-table-wrap">
            <table className="data-table tickets-data-table">
              <thead>
                <tr>
                  <th>Identificação</th>
                  <th>Descrição</th>
                  <th>Unidade</th>
                  <th>Status</th>
                  <th>Data Abertura</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((t) => (
                  <tr key={t.id} className="hover:bg-gray-50">
                    <td>{String(t.id).padStart(5, '0')}</td>
                    <td><span className="description-cell">{t.descricao}</span></td>
                    <td><small className="table-sub">{franchises.find((f) => f.id === t.franquia_id)?.unidade || `Unidade ${t.franquia_id}`}</small></td>
                    <td><span className={`status-badge ${statusClassMap[t.status] || ''}`}>{t.status}</span></td>
                    <td className="date-cell">{formatDate(t.criado_em)}</td>
                    <td>
                      <button className="table-action" aria-label="Abrir conversa" onClick={(e) => { e.stopPropagation(); viewTicket(t.id) }}><MessageCircle size={16} /></button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : isError ? (
          <div className="error-panel">{(error as Error).message}</div>
        ) : filtered.length ? (
          <div className="recent-table-wrap">
            <table className="data-table tickets-data-table">
              <thead>
                <tr>
                  <th>Identificação</th>
                  <th>Descrição</th>
                  <th>Unidade</th>
                  <th>Status</th>
                  <th>Data Abertura</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((t) => (
                  <tr key={t.id} className="hover:bg-gray-50">
                    <td>{String(t.id).padStart(5, '0')}</td>
                    <td><span className="description-cell">{t.descricao}</span></td>
                    <td><small className="table-sub">{franchises.find((f) => f.id === t.franquia_id)?.unidade || `Unidade ${t.franquia_id}`}</small></td>
                    <td><span className={`status-badge ${statusClassMap[t.status] || ''}`}>{t.status}</span></td>
                    <td className="date-cell">{formatDate(t.criado_em)}</td>
                    <td>
                      <button className="table-action" aria-label="Abrir conversa" onClick={(e) => { e.stopPropagation(); viewTicket(t.id) }}><MessageCircle size={16} /></button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state">
            <div className="empty-icon"><Filter size={22} /></div>
            <strong>Nenhum chamado encontrado</strong>
            <p>Altere os filtros ou abra uma nova solicitação.</p>
          </div>
        )}
      </section>
    </section>
  )
}