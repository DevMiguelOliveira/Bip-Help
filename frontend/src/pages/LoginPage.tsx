import { useState } from 'react'
import type { FormEvent } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { ArrowRight, Eye, EyeOff, LockKeyhole, Mail, ShieldCheck, Sparkles } from 'lucide-react'
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
          <p>Uma visão integrada dos chamados, franquias e conversas. Mais clareza para quem atende. Mais agilidade para quem precisa.</p>
          <div className="login-visual-card">
            <div className="visual-card-top"><span>VISÃO OPERACIONAL</span><span className="live-indicator"><i /> AO VIVO</span></div>
            <div className="visual-stats"><div><small>Central de atendimento</small><strong>Em um só lugar</strong></div><div className="visual-ring"><span>360°</span></div></div>
            <div className="visual-lines"><i /><i /><i /></div>
          </div>
        </div>
        <div className="login-left-footer"><span>© {new Date().getFullYear()} BIPManager</span><span>Plataforma de suporte e operações</span></div>
      </div>
      <div className="login-right">
        <div className="login-form-wrap">
          <div className="mobile-login-brand"><div className="brand-mark"><span>B</span><i /></div><strong>BIPManager</strong></div>
          <div className="login-heading"><span className="login-kicker">BEM-VINDO DE VOLTA</span><h2>Acesse sua conta</h2><p>Entre com suas credenciais para continuar.</p></div>
          <form onSubmit={submit} className="login-form">
            <label className="field-label" htmlFor="email">E-mail corporativo</label>
            <div className="input-wrap"><Mail size={18} /><input id="email" type="email" autoComplete="username" placeholder="voce@empresa.com.br" value={email} onChange={handleEmailChange} required /></div>
            <div className="password-label-row"><label className="field-label" htmlFor="password">Senha</label></div>
            <div className="input-wrap"><LockKeyhole size={18} /><input id="password" type={showPassword ? 'text' : 'password'} autoComplete="current-password" placeholder="Digite sua senha" value={password} onChange={handlePasswordChange} required /><button type="button" className="show-password" onClick={() => setShowPassword((v) => !v)} aria-label={showPassword ? 'Ocultar senha' : 'Mostrar senha'}>{showPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button></div>
            {error && <div className="form-error" role="alert">{error}</div>}
            <button className="primary-button login-submit" type="submit" disabled={loading}>{loading ? 'Autenticando…' : <>Entrar na plataforma <ArrowRight size={17} /></>}</button>
          </form>
          <div className="login-safe"><ShieldCheck size={17} /><span>Conexão segura com autenticação protegida</span></div>
          <div className="login-form-footer">Acesso destinado a usuários autorizados da rede.</div>
        </div>
      </div>
    </div>
  )
}
