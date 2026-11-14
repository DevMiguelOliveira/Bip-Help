import { useState, useEffect } from 'react'
import { Clock3 } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { getTickets } from '../services/data'
import { formatDate } from '../lib/format'
import type { Ticket } from '../types'

export default function QueuePage() {
  const { token } = useAuth()
  const [queue, setQueue] = useState<Ticket[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [unassignedCount, setUnassignedCount] = useState(0)
  const [summary, setSummary] = useState({ total: 0, waiting: 0, highestWait: 0, notified: 0 })

  useEffect(() => {
    async function loadQueue() {
      setIsLoading(true)
      try {
        const tickets = await getTickets(token!)
        const unassigned = tickets.filter((t) => !t.assignee_id && t.status === 'Aberto')

        setQueue(unassigned.sort((a, b) => new Date(a.criado_em).getTime() - new Date(b.criado_em).getTime()))
        setUnassignedCount(unassigned.length)

        // Summary calculations
        const total = unassigned.length
        const waiting = unassigned.length
        const highestWait = total > 0
          ? Math.max(...unassigned.map((t) => (new Date().getTime() - new Date(t.criado_em).getTime())))
          : 0
        const notified = Math.floor(total / 2)

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

  return (
    <section className="queue-page">
      <div className="max-w-7xl mx-auto p-4">
        {isLoading ? (
          <div className="skeleton-text h-64">
            <div className="h-6 w-full mb-3" />
            <div className="h-6 w-full mb-3" />
            <div className="h-6 w-full mb-3" />
          </div>
        ) : unassignedCount === 0 ? (
          <div className="text-center py-12">
            <div className="text-4xl text-muted-foreground mb-4">
              <Clock3 size={32} className="inline-block align-middle" />
              <span>Nenhum chamado não atribuído</span>
            </div>
            <p className="text-muted-foreground">
              Todos os chamados estão atribuídos ou o sistema está offline.
            </p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              {queue.map((t) => (
                <div
                  key={t.id}
                  className="rounded-lg border p-4 hover:shadow-lg transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-medium">{t.descricao}</h4>
                      <p className="text-sm text-muted-foreground mt-1">
                        {formatDate(t.criado_em)} • {t.status}
                      </p>
                    </div>
                    {!t.assignee_id && (
                      <span className="text-sm px-2 py-1 rounded bg-orange-100/30 text-orange-400">
                        <small>Não atribuído</small>
                      </span>
                    )}
                  </div>
                  <p className="mt-2 text-sm line-clamp-2">
                    {t.descricao}
                  </p>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="p-4 rounded-lg bg-blue-50/30">
                <div className="font-medium">Total</div>
                <div className="text-2xl font-bold text-blue-600">{summary.total}</div>
              </div>
              <div className="p-4 rounded-lg bg-green-50/30">
                <div className="font-medium">Não atribuídos</div>
                <div className="text-2xl font-bold text-green-600">{summary.waiting}</div>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t">
              <p className="text-sm text-muted-foreground">
                Atualizações a cada 30 segundos
              </p>
            </div>
          </>
        )}
      </div>
    </section>
  )
}