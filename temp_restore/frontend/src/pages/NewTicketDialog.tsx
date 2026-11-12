import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { X, Ticket, Send } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { createTicket } from '../services/data'
import type { Franchise } from '../types'

export default function NewTicketDialog({ franchises, onClose }: { franchises: Franchise[]; onClose: () => void }) {
  const { token } = useAuth()
  const queryClient = useQueryClient()
  const [franchiseId, setFranchiseId] = useState(franchises[0] ? String(franchises[0].id) : '')
  const [description, setDescription] = useState('')
  const mutation = useMutation({
    mutationFn: () => createTicket(token!, Number(franchiseId), description),
    onSuccess: async () => { await queryClient.invalidateQueries({ queryKey: ['tickets'] }); onClose() },
  })
  return <div className="modal-backdrop" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose() }}><div className="modal-card"><div className="modal-heading"><div className="modal-icon"><Ticket size={19} /></div><div><h2>Abrir chamado</h2><p>Descreva a necessidade da unidade.</p></div><button className="icon-button modal-close" onClick={onClose}><X size={18} /></button></div><form onSubmit={(e) => { e.preventDefault(); mutation.mutate() }} className="modal-form"><label className="field-label">Unidade</label><select className="form-control" value={franchiseId} onChange={(e) => setFranchiseId(e.target.value)} required><option value="" disabled>Selecione uma unidade</option>{franchises.map((f) => <option key={f.id} value={f.id}>{f.unidade}</option>)}</select><label className="field-label">Descrição do problema</label><textarea className="form-control textarea-control" placeholder="Conte o que aconteceu, em qual equipamento ou processo…" value={description} onChange={(e) => setDescription(e.target.value)} required minLength={1} maxLength={10000} rows={5} /><div className="form-hint">Inclua detalhes que ajudem o suporte a entender a ocorrência.</div>{mutation.isError && <div className="form-error">{mutation.error.message}</div>}<div className="modal-actions"><button type="button" className="secondary-button" onClick={onClose}>Cancelar</button><button type="submit" className="primary-button" disabled={mutation.isPending || !franchiseId || !description.trim()}>{mutation.isPending ? 'Enviando…' : <>Criar chamado <Send size={15} /></>}</button></div></form></div></div>
}
