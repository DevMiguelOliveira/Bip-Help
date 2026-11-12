import { apiJson, apiRequest } from '../lib/api'
import type { AttendantUpdate, Franchise, Message, TeamMember, Ticket, User } from '../types'

export function getFranchises(token: string) {
  return apiRequest<Franchise[]>('/franquias/?limit=500', {}, token)
}

export function getTickets(token: string, franchiseId?: number, status?: string) {
  const params = new URLSearchParams({ limit: '500' })
  if (franchiseId) params.set('franquia_id', String(franchiseId))
  // Status is filtered client-side because the current API does not expose a status query parameter.
  void status
  return apiRequest<Ticket[]>(`/tickets/?${params.toString()}`, {}, token)
}

export function getMessages(token: string, ticketId: number) {
  return apiRequest<Message[]>(`/tickets/${ticketId}/mensagens/`, {}, token)
}

export function createTicket(token: string, franchiseId: number, description: string) {
  return apiJson<Ticket>('/tickets/', 'POST', { franquia_id: franchiseId, descricao: description }, token)
}

export function sendMessage(token: string, ticketId: number, text: string, file?: File) {
  const body = new FormData()
  if (text.trim()) body.append('texto', text.trim())
  if (file) body.append('file', file)
  return apiRequest<Message>(`/tickets/${ticketId}/mensagens/`, { method: 'POST', body }, token)
}

export function getUsers(token: string) {
  return apiRequest<User[]>('/usuarios/?limit=500', {}, token)
}

export function createUser(token: string, user: { nome: string; email: string; senha: string; perfil_sistema: 'administrador' | 'suporte_n1' | 'suporte_n2' | null }) {
  return apiJson<User>('/usuarios/', 'POST', user, token)
}

export function linkUserToFranchise(token: string, userId: number, franchiseId: number, papel: 'proprietario' | 'gerente' | 'funcionario') {
  return apiJson(`/usuarios/${userId}/franquias`, 'POST', { franquia_id: franchiseId, papel }, token)
}

export function deactivateUserFranchise(token: string, userId: number, franchiseId: number) {
  return apiRequest(`/usuarios/${userId}/franquias/${franchiseId}`, { method: 'DELETE' }, token)
}

export function updateTicket(token: string, ticketId: number, data: { status?: string; descricao?: string }) {
  return apiJson<Ticket>(`/tickets/${ticketId}`, 'PATCH', data, token)
}


export function getTeam(token: string) {
  return apiRequest<TeamMember[]>('/equipe/', {}, token)
}

export function updateAttendant(token: string, userId: number, data: AttendantUpdate) {
  return apiJson<TeamMember>(`/equipe/${userId}`, 'PATCH', data, token)
}
