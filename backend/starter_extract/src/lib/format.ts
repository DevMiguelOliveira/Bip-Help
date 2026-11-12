import type { TicketStatus } from '../types'

export function formatDate(value: string) {
  return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short' }).format(new Date(value))
}
export function formatDateTime(value: string) {
  return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(value))
}
export function statusClass(status: TicketStatus) {
  if (status === 'Aberto') return 'status-amber'
  if (status === 'Em Atendimento') return 'status-blue'
  return 'status-green'
}
