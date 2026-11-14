import type { ApiError } from '../types'

const configuredBase = (import.meta.env.VITE_API_URL as string | undefined)?.trim()
export const API_BASE = configuredBase ? configuredBase.replace(/\/$/, '') : ''

export class ApiRequestError extends Error {
  status: number
  payload: unknown
  constructor(status: number, message: string, payload?: unknown) {
    super(message)
    this.name = 'ApiRequestError'
    this.status = status
    this.payload = payload
  }
}

let unauthorizedHandler: (() => void) | undefined
export function setUnauthorizedHandler(handler: () => void) {
  unauthorizedHandler = handler
}

// Armazena o papel do usuário atual para mensagens de erro personalizadas
let currentUserRole: string | null = null
export function setCurrentUserRole(role: string | null) {
  currentUserRole = role
}

// Mensagens de erro amigáveis por papel do usuário
function getFriendlyErrorMessage(status: number, detail: string, role: string | null): string {
  // Mensagens base do backend (detail)
  const backendMessage = detail || `Falha na solicitação (${status}).`

  // Se não há papel definido, retorna mensagem padrão
  if (!role) return backendMessage

  switch (status) {
    case 401: // Unauthorized - Sessão expirada ou token inválido
      if (role === 'administrador' || role === 'suporte_n1' || role === 'suporte_n2') {
        return 'Sessão expirada. Por favor, faça login novamente.'
      }
      return 'Sua sessão expirou. Por favor, faça login novamente.'

    case 403: // Forbidden - Permissão negada
      if (role === 'administrador') {
        return 'Acesso administrativo negado. Verifique suas permissões.'
      }
      if (role === 'suporte_n1' || role === 'suporte_n2') {
        return 'Você não tem permissão para realizar esta operação.'
      }
      return 'Permissão negada. Você não tem acesso a este recurso.'

    case 404: // Not Found
      return 'O recurso solicitado não foi encontrado.'

    case 409: // Conflict
      return `Conflito: ${backendMessage}`

    case 422: // Unprocessable Entity - Validation errors
      return `Dados inválidos: ${backendMessage}`

    case 500: // Internal Server Error
      if (role === 'administrador' || role === 'suporte_n1' || role === 'suporte_n2') {
        return 'Erro interno do servidor. Verifique os logs ou tente novamente.'
      }
      return 'Ocorreu um erro interno. Tente novamente em alguns instantes.'

    default:
      return backendMessage
  }
}

export function apiUrl(path: string) {
  return `${API_BASE}${path.startsWith('/') ? path : `/${path}`}`
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (response.status === 401) unauthorizedHandler?.()
  if (!response.ok) {
    let payload: ApiError | undefined
    try { payload = await response.json() as ApiError } catch { /* body may not be JSON */ }

    // Mensagem de erro personalizada por papel do usuário
    const detail = payload?.detail || ''
    const friendlyMessage = getFriendlyErrorMessage(response.status, detail, currentUserRole)

    throw new ApiRequestError(response.status, friendlyMessage, payload)
  }
  if (response.status === 204) return undefined as T
  const contentType = response.headers.get('content-type') || ''
  if (contentType.includes('application/json')) return response.json() as Promise<T>
  return response.text() as Promise<T>
}

export async function apiRequest<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const headers = new Headers(options.headers)
  if (token) headers.set('Authorization', `Bearer ${token}`)
  if (options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  // Timeout explícito de 15 segundos para todas as requisições HTTP
  const timeoutPromise = new Promise<never>((_, reject) =>
    setTimeout(() => reject(new Error('Timeout de 15s na requisição HTTP')), 15_000)
  )

  const response = await Promise.race([
    fetch(apiUrl(path), {
      ...options,
      headers,
      credentials: 'same-origin',
    }),
    timeoutPromise
  ])

  return parseResponse<T>(response)
}

export async function apiJson<T>(path: string, method: string, body: unknown, token: string): Promise<T> {
  return apiRequest<T>(path, { method, body: JSON.stringify(body) }, token)
}

export async function privateFileUrl(path: string, token: string): Promise<string> {
  const response = await fetch(apiUrl(path), {
    headers: { Authorization: `Bearer ${token}` },
    credentials: 'same-origin',
  })
  if (response.status === 401) unauthorizedHandler?.()
  if (!response.ok) throw new ApiRequestError(response.status, 'Não foi possível carregar o anexo.')
  return URL.createObjectURL(await response.blob())
}
