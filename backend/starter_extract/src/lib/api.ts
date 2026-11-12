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

export function apiUrl(path: string) {
  return `${API_BASE}${path.startsWith('/') ? path : `/${path}`}`
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (response.status === 401) unauthorizedHandler?.()
  if (!response.ok) {
    let payload: ApiError | undefined
    try { payload = await response.json() as ApiError } catch { /* body may not be JSON */ }
    throw new ApiRequestError(response.status, payload?.detail || `Falha na solicitação (${response.status}).`, payload)
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
  const response = await fetch(apiUrl(path), {
    ...options,
    headers,
    credentials: 'same-origin',
  })
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
