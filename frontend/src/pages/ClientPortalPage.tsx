import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ArrowRight, Clock3, MessageCircle, Plus, Ticket as TicketIcon } from 'lucide-react'
import { Link, useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getFranchises, getTickets } from '../services/data'
import NewTicketDialog from './NewTicketDialog'
import TicketChatDialog from './TicketChatDialog'
import { formatDate, statusClass } from '../lib/format'

export default function ClientPortalPage() {
  const { token, user } = useAuth()
  const [showNew, setShowNew] = useState(false)
  const [params, setParams] = useSearchParams()
  const { data: franchises = [] } = useQuery({ queryKey: ['franchises'], queryFn: () => getFranchises(token!), enabled: !!token })
  const { data: tickets = [], isLoading, isError, error } = useQuery({ queryKey: ['tickets'], queryFn: () => getTickets(token!), enabled: !!token })
  const recent = useMemo(() => [...tickets].sort((a, b) => new Date(b.criado_em).getTime() - new Date(a.criado_em).getTime()).slice(0, 5), [tickets])
  const selectedId = Number(params.get('selected')) || null
  const selectedTicket = selectedId ? tickets.find((ticket) => ticket.id === selectedId) : undefined
  const closeTicket = () => setParams({})
  const opened = tickets.filter((ticket) => ticket.status === 'Aberto').length
  const active = tickets.filter((ticket) => ticket.status === 'Em Atendimento').length
  const firstName = user?.nome?.trim().split(/\s+/)[0] || 'bem-vindo'

  return <div className="page-stack client-home">
    <section className="client-welcome-card">
      <div className="client-welcome-copy">
        <span className="eyebrow muted-eyebrow">PORTAL DE ATENDIMENTO</span>
        <h1>Olá, {firstName}.</h1>
        <p>Como podemos ajudar sua unidade hoje?</p>
        <button className="primary-button client-primary-action" onClick={() => setShowNew(true)}><Plus size={17} /> Abrir novo chamado</button>
      </div>
      <div className="client-welcome-art"><div className="client-art-circle"><MessageCircle size={42} /></div><span>Estamos aqui para ajudar</span></div>
    </section>

    <section className="client-stat-grid">
      <div className="client-stat-card"><span className="client-stat-icon blue"><TicketIcon size={18}/></span><div><strong>{tickets.length}</strong><span>Meus chamados</span></div></div>
      <div className="client-stat-card"><span className="client-stat-icon amber"><Clock3 size={18}/></span><div><strong>{opened}</strong><span>Aguardando atendimento</span></div></div>
      <div className="client-stat-card"><span className="client-stat-icon violet"><MessageCircle size={18}/></span><div><strong>{active}</strong><span>Em atendimento</span></div></div>
    </section>

    <section className="panel client-recent-panel">
      <div className="panel-heading"><div><span className="section-kicker">ACOMPANHAMENTO</span><h2>Seus chamados recentes</h2><p>Acompanhe as respostas e o andamento das suas solicitações.</p></div><Link to="/tickets" className="text-link">Ver todos <ArrowRight size={15}/></Link></div>
      {isLoading ? <div className="loading-panel">Carregando seus chamados…</div> : isError ? <div className="error-panel">{(error as Error).message}</div> : recent.length ? <div className="client-ticket-list">
        {recent.map((ticket) => <button className="client-ticket-row" key={ticket.id} onClick={() => setParams({ selected: String(ticket.id) })}>
          <span className="client-ticket-icon"><TicketIcon size={18}/></span>
          <span className="client-ticket-main"><strong>Chamado #{String(ticket.id).padStart(5, '0')}</strong><small>{ticket.descricao}</small><small>{franchises.find((item) => item.id === ticket.franquia_id)?.unidade || `Unidade ${ticket.franquia_id}`} · {formatDate(ticket.criado_em)}</small></span>
          <span className={`status-badge ${statusClass(ticket.status)}`}>{ticket.status}</span>
          <ArrowRight className="client-row-arrow" size={16}/>
        </button>)}
      </div> : <div className="client-empty-state"><div className="empty-icon"><MessageCircle size={22}/></div><strong>Você ainda não possui chamados</strong><p>Quando precisar de ajuda, abra uma solicitação por aqui.</p><button className="secondary-button" onClick={() => setShowNew(true)}><Plus size={15}/> Abrir primeiro chamado</button></div>}
    </section>
    <section className="client-help-strip"><MessageCircle size={19}/><div><strong>Converse diretamente com nossa equipe</strong><span>Abra um chamado para iniciar uma conversa com o suporte e acompanhar todas as atualizações.</span></div></section>
    {showNew && <NewTicketDialog franchises={franchises} onClose={() => setShowNew(false)} />}
    {selectedTicket && <TicketChatDialog ticket={selectedTicket} onClose={closeTicket} />}
  </div>
}
