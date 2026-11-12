export type SystemRole = 'administrador' | 'suporte_n1' | null
export type FranchiseRole = 'proprietario' | 'gerente' | 'funcionario'
export type TicketStatus = 'Aberto' | 'Em Atendimento' | 'Encerrado'

export interface Franchise {
  id: number
  nome_responsavel: string
  unidade: string
  telefone: string
  ativa: boolean
}

export interface UserFranchise {
  franquia_id: number
  unidade: string
  nome_responsavel: string
  papel: FranchiseRole
  ativa: boolean
}

export interface User {
  id: number
  nome: string
  email: string
  perfil_sistema: SystemRole
  ativo: boolean
  criado_em: string
  franquias?: UserFranchise[]
}

export interface Ticket {
  id: number
  franquia_id: number
  descricao: string
  status: TicketStatus
  criado_em: string
}

export interface Message {
  id: number
  ticket_id: number
  remetente: string
  remetente_id?: number
  texto: string | null
  url_anexo: string | null
  criada_em: string
}

export interface ApiError {
  detail?: string
}
