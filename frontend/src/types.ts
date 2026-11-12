export type SystemRole = 'administrador' | 'suporte_n1' | 'suporte_n2' | null
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

export interface TeamMember {
  usuario_id: number
  nome: string
  email: string
  perfil_sistema: 'suporte_n1' | 'suporte_n2'
  ativo: boolean
  disponivel: boolean
  capacidade_maxima: number
  atualizado_em: string
}

export interface AttendantUpdate {
  disponivel?: boolean
  capacidade_maxima?: number
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
  remetente_id: number | null
  texto: string | null
  url_anexo: string | null
interna: boolean
  criada_em: string
}

export interface ApiError {
  detail?: string
}
