import { useState } from 'react'
import type { FormEvent } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { Eye, EyeOff } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { ApiRequestError } from '../lib/api'

export default function LoginPage() {
  const { login, loading } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [isHovering, setIsHovering] = useState(false)

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    try {
      await login(email, password)
      const destination = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname || '/'
      navigate(destination, { replace: true })
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : 'Não foi possível autenticar. Verifique sua conexão.')
    }
  }

  function handleEmailChange(e: React.ChangeEvent<HTMLInputElement>) {
    setEmail(e.target.value)
  }

  function handlePasswordChange(e: React.ChangeEvent<HTMLInputElement>) {
    setPassword(e.target.value)
  }

  return (
    <div className="login-screen">
      <div className="login-left">
        <div className="login-brand"><div className="brand-mark"><span>B</span><i /></div><strong>BIPManager</strong></div>
        <div className="login-hero">
          <div className="eyebrow"><Sparkles size={14} /> GESTÃO INTELIGENTE DE SUPORTE</div>
          <h1>O suporte conectado.<br /><span>A operação em movimento.</span></h1>
          <p>Uma visão integrada dos chamados, franquias e conversas. Mais c</p>
        </div>
      </div>
      <div className="login-right">
        <div className="login-card">
          <div className="login-header">
            <div>
              <h2>Entrar na conta</h2>
            </div>
          </div>
          <form className="login-form" onSubmit={submit}>
            <div className="form-group">
              <label htmlFor="email" className="form-label">E-mail</label>
              <input
                id="email"
                type="email"
                className="form-input"
                placeholder="seu@email.com"
                value={email}
                onChange={handleEmailChange}
              />
            </div>
            <div className="form-group">
              <label htmlFor="password" className="form-label">Senha</label>
              <div className="form-input-wrapper">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  className="form-input"
                  placeholder="Digite sua senha"
                  value={password}
                  onChange={handlePasswordChange}
                />
                <button
                  type="button"
                  className="toggle-password"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? EyeOff : Eye}
                </button>
              </div>
            </div>
            {error && <div className="error-message">{error}</div>}
            <button type="submit" className="submit-button">
              Entrar
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}