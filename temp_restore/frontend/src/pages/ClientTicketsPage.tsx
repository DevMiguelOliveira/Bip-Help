import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { MessageCircle, Plus, Search, Ticket as TicketIcon } from 'lucide-react'
import { useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getFranchises, getTickets } from '../services/data'
import NewTicketDialog from './NewTicketDialog'
import TicketChatDialog from './TicketChatDialog'
import { formatDate, statusClass } from '../lib/format'

export default function ClientTicketsPage() {
  const { token } = useAuth()
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('all')
  const [showNew, setShowNew] = useState(false)
  const [params, setParams] = useSearchParams()
  const { data: franchises = [] } = useQuery({ queryKey: ['franchises'], queryFn: () => getFranchises(token!), enabled: !!token })
  const { data: tickets = [], isLoading, isError, error } = useQuery({ queryKey: ['tickets'], queryFn: () => getTickets(token!), enabled: !!token })
  const filtered = useMemo(() => tickets.filter((ticket) => {
    const matchesSearch = !search || String(ticket.id).includes(search) || ticket.descricao.toLowerCase().includes(search.toLowerCase())
    return matchesSearch && (status === 'all' || ticket.status === status)
  }).sort((a, b) => new Date(b.criado_em).getTime() - new Date(a.criado_em).getTime()), [tickets, search, status])
  const selectedId = Number(params.get('selected')) || null
  const selectedTicket = selectedId ? tickets.find((ticket) => ticket.id === selectedId) : undefined

  return <div className="page-stack">
    <section className="welcome-row"><div><div className="eyebrow muted-eyebrow">PORTAL DE ATENDIMENTO</div><h1>Meus chamados</h1><p>Consulte suas solicitações e converse com a equipe de suporte.</p></div><button className="primary-button" onClick={() => setShowNew(true)}><Plus size={17}/> Novo chamado</button></section>
    <section className="panel client-list-panel">
      <div className="client-list-toolbar"><div className="search-field"><Search size={17}/><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar por número ou descrição…"/></div><select className="select-control" value={status} onChange={(event) => setStatus(event.target.value)}><option value="all">Todos os status</option><option>Aberto</option><option>Em Atendimento</option><option>Encerrado</option></select></div>
      {isLoading ? <div className="loading-panel">Carregando chamados…</div> : isError ? <div className="error-panel">{(error as Error).message}</div> : filtered.length ? <div className="client-ticket-list">
        {filtered.map((ticket) => <button className="client-ticket-row" key={ticket.id} onClick={() => setParams({ selected: String(ticket.id) })}>
          <span className="client-ticket-icon"><TicketIcon size={18}/></span>
          <span className="client-ticket-main"><strong>Chamado #{String(ticket.id).padStart(5, '0')}</strong><small>{ticket.descricao}</small><small>{franchises.find((item) => item.id === ticket.franquia_id)?.unidade || `Unidade ${ticket.franquia_id}`} · {formatDate(ticket.criado_em)}</small></span>
          <span className={`status-badge ${statusClass(ticket.status)}`}>{ticket.status}</span><MessageCircle className="client-row-arrow" size={17}/>
        </button>)}
      </div> : <div className="client-empty-state"><div className="empty-icon"><TicketIcon size={22}/></div><strong>Nenhum chamado encontrado</strong><p>Experimente alterar a busca ou abrir uma nova solicitação.</p></div>}
    </section>
    {showNew && <NewTicketDialog franchises={franchises} onClose={() => setShowNew(false)} />}
    {selectedTicket && <TicketChatDialog ticket={selectedTicket} onClose={() => setParams({})} />}
  </div>
}
