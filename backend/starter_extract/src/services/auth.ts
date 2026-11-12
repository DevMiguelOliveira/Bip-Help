import { apiRequest } from '../lib/api'
import type { User } from '../types'

export interface LoginResult {
  access_token: string
  token_type: 'bearer'
  expires_in: number
}

export async function login(email: string, password: string) {
  const body = new URLSearchParams({ username: email, password })
  return apiRequest<LoginResult>('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  })
}

export function getMe(token: string) {
  return apiRequest<User>('/auth/me', {}, token)
}
