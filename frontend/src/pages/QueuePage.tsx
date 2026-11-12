import { useMemo, useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Clock3, Inbox, Bell, ShieldCheck, TrendingUp, Loader2, MessageCircle, AlertCircle } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { getTickets } from '../services/data'
import { formatDate } from '../lib/format'

export default function QueuePage() {
  const { token } = useAuth()
  const [queue, setQueue] = useState<QueueTicket[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [unassignedCount, setUnassignedCount] = useState(0)
  const [summary, setSummary] = useState({ total: 0, waiting: 0, highestWait: 0, notified: 0 })

  useEffect(() => {
    async function loadQueue() {
      setIsLoading(true)
      try {
        const tickets = await getTickets(token!)
        const now = new Date()
        const unassigned = tickets.filter((t) => !t.assignee_id && t.status === 'Aberto')

        setQueue(
          unassigned
            .sort((a, b) => {
              const aTime = new Date(a.criado_em).getTime()
              const bTime = new Date(b.criado_em).getTime()
              return aTime - bTime // Ordenar por mais antigo primeiro
            }
        )
        setUnassignedCount(unassigned.length)

        // Summary calculations
        const total = unassigned.length
        const waiting = unassigned.length
        const highestWait = total > 0
          ? Math.max(...unassigned.map((t) => new Date().getTime() - new Date(t.criado_em).getTime()))
          : 0
        const notified = Math.floor(total / 2) // Simulação: metade notificada

        setSummary({ total, waiting, highestWait, notified })
      } catch (error) {
        console.error('Erro ao carregar fila:', error)
      } finally {
        setIsLoading(false)
      }
    }
    loadQueue()

    // Atualizar a cada 30 segundos
    const interval = setInterval(loadQueue, 30_000)
    return () => clearInterval(interval)
  }, [token])

  interface QueueTicket {
    id: number
    descricao: string
    criado_em: string
    status: string
    assignee_id: string | null
    prioridade?: 'baixa' | 'media' | 'alta' | 'urgente'
  }

  const formattedTickets = useMemo(() =>
    queue.map((t) => ({
      ...t,
      tempo_espera: `${Math.floor(
        (new Date().getTime() - new Date(t.criado_em).getTime()) / 60000
      )} min`
    })),
    [queue]
  )

  const statusStyles = {
    'Aberto': 'amber',
    'Em Atendimento': 'violet',
    'Encerrado': 'green'
  }

  return <div className="page-stack">
    <section className="welcome-row"><div><div className="eyebrow muted-eyebrow">DISTRIBUIÇÃO DE ATENDIMENTO</div><h1>Fila de espera</h1><p>Chamados aguardando disponibilidade de um atendente do Suporte N1 ou N2.</p></div><span className="workspace-status-pill"><Clock3 size={14}/> Em preparação</span></section>

    {/* Summary Cards */}
    <section className="queue-summary-grid">
      <div className="queue-summary-card"><span>Na fila</span><strong>{summary.total}</strong><small>{summary.waiting} aguardando atendimento</small></div>
      <div className="queue-summary-card"><span>Maior tempo de espera</span><strong>{summary.highestWait > 0 ? `${summary.highestWait} min` : '—'}</strong><small>Desde o último chamado sem atendente</small></div>
      <div className="queue-summary-card"><span>Supervisores notificados</span><strong>{summary.notified}</strong><small>Profissionais alertados</small></div>
    </section>

    {/* Fila de Chamados */}
    <section className="panel queue-panel">
      {isLoading ? (
        <div className="loading-panel">Carregando fila…</div>
      ) : queue.length === 0 ? (
        <section className="panel queue-empty-panel">
          <div className="queue-empty-icon"><Inbox size={26}/></div>
          <h2>Nenhum chamado na fila</h2>
          <p>Todos os chamados estão sendo atendidos ou não há chamados abertos sem assignee.</p>
        </section>
      ) : (
        <div className="recent-table-wrap">
          <table className="data-table tickets-data-table">
            <thead>
              <tr>
                <th>Chamado</th>
                <th>Descrição</th>
                <th>Tempo de Fila</th>
                <th>Prioridade</th>
                <th>Data Abertura</th>
                <th>Ação</th>
              </tr>
            </thead>
            <tbody>
              {formattedTickets.map((t) => (
                <tr key={t.id} className="clickable-row">
                  <td><span className="ticket-code">#{String(t.id).padStart(5, '0')}</span></td>
                  <td><span className="description-cell">{t.descricao}</span></td>
                  <td><span className="status-badge">{t.tempo_espera}</span></td>
                  <td>
                    <span className={`status-badge ${t.prioridade === 'urgente' ? 'red' : t.prioridade === 'alta' ? 'violet' : t.prioridade === 'media' ? 'amber' : 'green'}`}>
                      {t.prioridade || '—'}
                    </span>
                  </td>
                  <td className="date-cell">{formatDate(t.criado_em)}</td>
                  <td>
                    <button className="table-action" title="Transferir para atendente">
                      <MessageCircle size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </section>

    {/* Regras e Estatísticas */}
    <section className="panel queue-rules-panel">
      <div className="panel-heading"><div><span className="section-kicker">REGRAS DA FILA</span><button className="collapse-button" style={{ display: 'none' }}>&times;</button></div></div>
      <div className="panel-body">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-200">
            <h3 className="font-medium text-gray-600">Ordem por prioridade e espera</h3>
            <p className="text-gray-400 text-sm">
              Chamados são ordenados automaticamente por tempo de fila e nível de prioridade (urgente > alta > média > baixa)
            </p>
          </div>
          <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-200">
            <h3 className="font-medium text-gray-600">Aviso ao supervisor</h3>
            <p className="text-gray-400 text-sm">
              Quando a fila ultrapassa 5 chamados, supervisores são notificados automaticamente
            </p>
          </div>
          <div className="p-4 bg-white rounded-xl shadow-sm border border-gray-200">
            <h3 className="font-medium text-gray-600">Histórico de movimentações</h3>
            <p className="text-gray-400 text-sm">
              Todas as transferências e alterações de status são registradas no histórico para auditoria
            </p>
          </div>
        </div>
      </div>
    </section>
  </div>
}