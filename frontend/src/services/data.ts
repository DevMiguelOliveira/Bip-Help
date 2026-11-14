import { apiJson, apiRequest } from '../lib/api'
import type { AttendantUpdate, Franchise, Message, TeamMember, Ticket, User } from '../types'

export function getFranchises(token: string, params?: { skip?: number; limit?: number }) {
  const searchParams = new URLSearchParams()
  if (params) {
    if (params.skip !== undefined) searchParams.set('skip', String(params.skip))
    if (params.limit !== undefined) searchParams.set('limit', String(params.limit))
  } else {
    searchParams.set('limit', '50')
  }
  return apiRequest<Franchise[]>(`/franquias/?${searchParams.toString()}`, {}, token)
}

export function getTickets(token: string, franchiseId?: number, status?: string, params?: { skip?: number; limit?: number }) {
  const searchParams = new URLSearchParams()
  searchParams.set('limit', String(params?.limit ?? 50))
  if (params?.skip !== undefined) searchParams.set('skip', String(params.skip))
  if (franchiseId !== undefined) searchParams.set('franquia_id', String(franchiseId))
  if (status !== undefined && status !== 'all') searchParams.set('status', status)
  return apiRequest<Ticket[]>(`/tickets/?${searchParams.toString()}`, {}, token)
}

export function getMessages(token: string, ticketId: number) {
  return apiRequest<Message[]>(`/tickets/${ticketId}/mensagens/`, {}, token)
}

export function getMessage(token: string, mensagemId: number) {
  return apiRequest<Message>(`/mensagens/${mensagemId}`, {}, token)
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
