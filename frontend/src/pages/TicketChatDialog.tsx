import { useEffect, useMemo, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { FileImage, LoaderCircle, MessageCircle, Paperclip, Send, ShieldCheck, X } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { apiRequest, privateFileUrl } from '../lib/api'
import { getMessages, sendMessage, updateTicket, getMessage } from '../services/data'
import type { Message, Ticket } from '../types'
import { formatDateTime, statusClass } from '../lib/format'

interface WsToken { token: string; expires_in: number; created_at: number }
interface SingleMessage { id: number; texto: string; url_anexo: string; interna: boolean; criado_em: string; remetente: string; remetente_id: number | null }

export default function TicketChatDialog({ ticket, onClose }: { ticket: Ticket; onClose: () => void }) {
  const { token, user } = useAuth()
  const queryClient = useQueryClient()
  const [text, setText] = useState('')
  const [file, setFile] = useState<File | undefined>()
  const [wsStatus, setWsStatus] = useState<'connecting' | 'connected' | 'offline'>('connecting')
  const [liveMessages, setLiveMessages] = useState<Message[]>([])
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputFileRef = useRef<HTMLInputElement>(null)
  const messagesQuery = useQuery({ queryKey: ['messages', ticket.id], queryFn: () => getMessages(token!, ticket.id), enabled: !!token })
  const statusMutation = useMutation({
    mutationFn: (nextStatus: string) => updateTicket(token!, ticket.id, { status: nextStatus }),
    onSuccess: async () => { await queryClient.invalidateQueries({ queryKey: ['tickets'] }) },
  })
  const mutation = useMutation({
    mutationFn: () => sendMessage(token!, ticket.id, text, file),
    onSuccess: async () => { setText(''); setFile(undefined); if (inputFileRef.current) inputFileRef.current.value = ''; await queryClient.invalidateQueries({ queryKey: ['messages', ticket.id] }) },
  })
  const messages = useMemo(() => [...(messagesQuery.data || []), ...liveMessages.filter((m) => !(messagesQuery.data || []).some((old) => old.id === m.id))], [messagesQuery.data, liveMessages])

  useEffect(() => {
    let active = true
    let socket: WebSocket | undefined
    let retryTimer: number | undefined
    let retryCount = 0
    let reconnectTimer: number | undefined
    let tokenCreatedAt = 0

    async function connect() {
      if (!active || !token) return
      setWsStatus('connecting')
      try {
        // Request new WS token from backend
        const result = await apiRequest<WsToken>(`/tickets/${ticket.id}/ws-token`, { method: 'POST' }, token)
        if (!active) return
        tokenCreatedAt = Date.now()

        const configured = (import.meta.env.VITE_WS_URL as string | undefined)?.trim()
        const wsBase = configured ? configured.replace(/\/$/, '') : `${location.protocol === 'https:' ? 'wss:' : 'ws:'}//${location.host}`
        socket = new WebSocket(`${wsBase}/ws/tickets/${ticket.id}`)
        socket.onopen = () => socket?.send(JSON.stringify({ type: 'authenticate', token: result.token }))
        socket.onmessage = (event) => {
          try {
            const payload = JSON.parse(event.data) as Record<string, unknown>
            if (payload.type === 'authenticated') { setWsStatus('connected'); retryCount = 0; return }
            if (payload.type === 'ticket_updated' && payload.ticket_id === ticket.id) {
              queryClient.invalidateQueries({ queryKey: ['tickets'] })
              return
            }
            if (payload.type === 'new_message' && typeof payload.id === 'number') {
              setLiveMessages((old) => [...old, payload as unknown as Message])
              queryClient.invalidateQueries({ queryKey: ['messages', ticket.id] })
            }
          } catch { /* ignore malformed event */ }
        }
        socket.onclose = () => {
          setWsStatus('offline')
          if (!active) return
          // Check if we should refresh token before reconnecting
          const timeSinceToken = Date.now() - tokenCreatedAt
          const shouldRefresh = timeSinceToken > 45_000 // Refresh at 45s (before 60s expiry)
          retryCount += 1
          const delay = Math.min(1000 * 2 ** Math.min(retryCount, 5), 30_000)
          // If token expired, force a refresh by requesting new token on next connect
          retryTimer = window.setTimeout(connect, shouldRefresh ? 100 : delay)
        }
        socket.onerror = () => socket?.close()
      } catch {
        setWsStatus('offline')
        if (active) {
          retryCount += 1
          reconnectTimer = window.setTimeout(connect, Math.min(1000 * 2 ** Math.min(retryCount, 5), 30_000))
        }
      }
    }
    void connect()

    // Proactive token renewal: refresh 10 seconds before expiry (50s into 60s lifetime)
    const renewalTimer = window.setInterval(async () => {
      if (!active || !socket || wsStatus !== 'connected') return
      const timeSinceToken = Date.now() - tokenCreatedAt
      // Refresh when within 10 seconds of expiry
      if (timeSinceToken > 50_000) {
        try {
          await apiRequest<WsToken>(`/tickets/${ticket.id}/ws-token`, { method: 'POST' }, token)
          tokenCreatedAt = Date.now()
        } catch {
          // Token refresh failed, will reconnect on next error
        }
      }
    }, 5_000) // Check every 5 seconds

    return () => {
      active = false
      if (retryTimer) clearTimeout(retryTimer)
      if (reconnectTimer) clearTimeout(reconnectTimer)
      if (renewalTimer) clearInterval(renewalTimer)
      socket?.close()
    }
  }, [token, ticket.id, queryClient])

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages.length])

  function submit(event: FormEvent) {
    event.preventDefault()
    if (!text.trim() && !file) return
    mutation.mutate()
  }

  return <div className="modal-backdrop chat-backdrop" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose() }}><section className="chat-dialog"><header className="chat-header"><div className="chat-ticket-icon"><MessageCircle size={19} /></div><div className="chat-title"><div><strong>Chamado #{String(ticket.id).padStart(5, '0')}</strong><span className={`status-badge ${statusClass(ticket.status)}`}>{ticket.status}</span></div><p>{ticket.descricao}</p></div><div className={`connection-state ${wsStatus}`}><i />{wsStatus === 'connected' ? 'Ao vivo' : wsStatus === 'connecting' ? 'Conectando' : 'Reconectando'}</div>{(user?.perfil_sistema === 'administrador' || user?.perfil_sistema === 'suporte_n1' || user?.perfil_sistema === 'suporte_n2') && <select className="select-control chat-status-select" aria-label="Alterar status do chamado" value={ticket.status} disabled={statusMutation.isPending} onChange={(e) => statusMutation.mutate(e.target.value)}><option>Aberto</option><option>Em Atendimento</option><option>Encerrado</option></select>}<button className="icon-button" onClick={onClose}><X size={19} /></button></header>
    <div className="chat-body">{messagesQuery.isLoading ? <div className="loading-panel">Carregando conversa…</div> : messages.length ? messages.map((message) => <MessageBubble key={message.id} message={message} own={message.remetente_id !== null && message.remetente_id === user?.id} token={token!} />) : <div className="chat-empty"><div className="empty-icon"><MessageCircle size={22} /></div><strong>Início da conversa</strong><p>Envie uma mensagem para iniciar o atendimento.</p></div>}<div ref={bottomRef} /></div>
    <form className="chat-composer" onSubmit={submit}><div className="composer-attachment">{file && <span className="attached-file"><FileImage size={14} /> {file.name} <button type="button" onClick={() => setFile(undefined)} aria-label="Remover anexo"><X size={13} /></button></span>}</div><div className="composer-row"><button type="button" className="icon-button attach-button" onClick={() => inputFileRef.current?.click()} title="Anexar imagem"><Paperclip size={18} /></button><input ref={inputFileRef} type="file" accept="image/jpeg,image/png,image/webp" hidden onChange={(e) => { const selected = e.target.files?.[0]; if (selected && selected.size <= 20 * 1024 * 1024) setFile(selected); else if (selected) alert('O arquivo ultrapassa o limite de 20 MB.') }} /><textarea value={text} onChange={(e) => setText(e.target.value)} placeholder="Escreva sua mensagem…" rows={1} maxLength={10000} /><button className="send-button" type="submit" disabled={mutation.isPending || (!text.trim() && !file)}>{mutation.isPending ? <LoaderCircle className="spin" size={17} /> : <Send size={17} />}</button></div>{statusMutation.isError && <p className="composer-error">{statusMutation.error.message}</p>}{mutation.isError && <p className="composer-error">{mutation.error.message}</p>}<div className="composer-foot"><span>Enter não envia automaticamente. Anexos JPG, PNG ou WEBP • até 20 MB.</span><span><ShieldCheck size={13} /> Conversa autenticada</span></div></form></section></div>
}

function MessageBubble({ message, own, token }: { message: Message; own: boolean; token: string }) {
  const [imageUrl, setImageUrl] = useState<string | null>(null)
  const [imageError, setImageError] = useState(false)
  useEffect(() => {
    let objectUrl: string | null = null
    let active = true
    if (message.url_anexo) {
      privateFileUrl(message.url_anexo, token).then((url) => { objectUrl = url; if (active) setImageUrl(url); else URL.revokeObjectURL(url) }).catch(() => { if (active) setImageError(true) })
    }
    return () => { active = false; if (objectUrl) URL.revokeObjectURL(objectUrl) }
  }, [message.url_anexo, token])
  return <div className={`message-row ${own ? 'own' : ''}`}><div className="message-avatar">{message.remetente.slice(0, 1).toUpperCase()}</div><div className="message-content"><div className="message-meta"><strong>{own ? 'Você' : message.remetente}</strong><time>{formatDateTime(message.criada_em)}</time></div><div className="message-bubble">{message.texto && <p>{message.texto}</p>}{message.url_anexo && (imageUrl ? <a href={imageUrl} target="_blank" rel="noreferrer"><img src={imageUrl} alt="Anexo do chamado" className="message-image" /></a> : imageError ? <span className="attachment-unavailable">Anexo indisponível</span> : <span className="attachment-loading"><LoaderCircle className="spin" size={14} /> Carregando anexo…</span>)}</div></div></div>
}