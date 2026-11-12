import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Activity, Users, UserCheck, UserX, ShieldCheck, RefreshCw, Save } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { getTeam, updateAttendant } from '../services/data'

export default function TeamPage() {
  const { token, user } = useAuth()
  const queryClient = useQueryClient()
  const [capacityDrafts, setCapacityDrafts] = useState<Record<number, string>>({})
  const [success, setSuccess] = useState('')
  const isAdmin = user?.perfil_sistema === 'administrador'

  const team = useQuery({
    queryKey: ['team'],
    queryFn: () => getTeam(token!),
    enabled: !!token,
  })

  const mutation = useMutation({
    mutationFn: ({ userId, data }: { userId: number; data: { disponivel?: boolean; capacidade_maxima?: number } }) =>
      updateAttendant(token!, userId, data),
    onSuccess: async (_updated, variables) => {
      setSuccess(variables.data.capacidade_maxima !== undefined
        ? 'Capacidade do atendente atualizada.'
        : 'Disponibilidade atualizada.')
      await queryClient.invalidateQueries({ queryKey: ['team'] })
    },
  })

  const members = team.data || []
  const n1 = members.filter((member) => member.perfil_sistema === 'suporte_n1')
  const n2 = members.filter((member) => member.perfil_sistema === 'suporte_n2')
  const available = members.filter((member) => member.ativo && member.disponivel).length

  function saveCapacity(userId: number, currentCapacity: number) {
    const raw = capacityDrafts[userId] ?? String(currentCapacity)
    const capacity = Number(raw)
    if (!Number.isInteger(capacity) || capacity < 1) {
      setSuccess('')
      return
    }
    mutation.mutate({ userId, data: { capacidade_maxima: capacity } })
  }

  return <div className="page-stack">
    <section className="welcome-row">
      <div>
        <div className="eyebrow muted-eyebrow">OPERAÇÃO INTERNA</div>
        <h1>Equipe de suporte</h1>
        <p>Gerencie a disponibilidade e a capacidade individual dos atendentes N1 e N2.</p>
      </div>
      <div className="welcome-actions">
        <button className="secondary-button" onClick={() => team.refetch()} disabled={team.isFetching}>
          <RefreshCw size={16} /> {team.isFetching ? 'Atualizando…' : 'Atualizar'}
        </button>
      </div>
    </section>

    {success && <div className="success-banner"><ShieldCheck size={17} /> {success}</div>}
    {team.isError && <div className="form-error">{team.error.message}</div>}
    {mutation.isError && <div className="form-error">{mutation.error.message}</div>}

    <section className="team-level-grid">
      <article className="team-level-card team-n1">
        <div className="team-level-heading"><span className="team-level-icon"><Users size={20}/></span><span className="status-badge status-blue">Nível 1</span></div>
        <h2>Suporte N1</h2>
        <p>Primeiro atendimento, dúvidas operacionais e procedimentos conhecidos.</p>
        <div className="team-level-footer"><span><UserCheck size={15}/> Atendentes cadastrados</span><strong>{team.isLoading ? '—' : n1.length}</strong></div>
      </article>
      <article className="team-level-card team-n2">
        <div className="team-level-heading"><span className="team-level-icon"><Activity size={20}/></span><span className="status-badge status-gray">Nível 2</span></div>
        <h2>Suporte N2</h2>
        <p>Análises avançadas e chamados escalonados pelo primeiro nível.</p>
        <div className="team-level-footer"><span><UserCheck size={15}/> Atendentes cadastrados</span><strong>{team.isLoading ? '—' : n2.length}</strong></div>
      </article>
    </section>

    <section className="user-summary-grid">
      <div className="mini-stat"><span className="mini-stat-icon green"><UserCheck size={17} /></span><div><strong>{team.isLoading ? '—' : available}</strong><small>Disponíveis e ativos</small></div></div>
      <div className="mini-stat"><span className="mini-stat-icon blue"><Users size={17} /></span><div><strong>{team.isLoading ? '—' : members.length}</strong><small>Total de atendentes</small></div></div>
      <div className="mini-stat"><span className="mini-stat-icon violet"><ShieldCheck size={17} /></span><div><strong>10</strong><small>Capacidade padrão inicial</small></div></div>
    </section>

    <section className="panel workspace-panel">
      <div className="panel-heading">
        <div><span className="section-kicker">GESTÃO DE CAPACIDADE</span><h2>Disponibilidade dos atendentes</h2><p>O limite inicial é de 10 chamados ativos por atendente. O administrador pode ajustar o limite individual.</p></div>
        <Users className="heading-icon" size={20}/>
      </div>

      {team.isLoading ? <div className="loading-panel">Carregando equipe…</div> : members.length === 0 ? (
        <div className="team-empty-state"><UserX size={24}/><strong>Nenhum atendente cadastrado</strong><span>Cadastre usuários com perfil Suporte N1 ou Suporte N2 na área de Usuários.</span></div>
      ) : (
        <div className="team-attendant-list">
          {members.map((member) => {
            const isMe = user?.id === member.usuario_id
            const canChangeAvailability = isAdmin || isMe
            const isAvailable = member.ativo && member.disponivel
            return <article className="team-attendant-row" key={member.usuario_id}>
              <div className="avatar user-row-avatar">{member.nome.split(/\s+/).slice(0, 2).map((part) => part[0]).join('').toUpperCase()}</div>
              <div className="team-attendant-identity">
                <strong>{member.nome}{isMe ? ' (você)' : ''}</strong>
                <small>{member.email}</small>
                <span className={`status-badge ${member.perfil_sistema === 'suporte_n1' ? 'status-blue' : 'status-gray'}`}>{member.perfil_sistema === 'suporte_n1' ? 'Suporte N1' : 'Suporte N2'}</span>
              </div>
              <div className="team-attendant-status">
                <span className={`status-badge ${!member.ativo ? 'status-gray' : isAvailable ? 'status-green' : 'status-gray'}`}>
                  {!member.ativo ? 'Conta inativa' : isAvailable ? 'Disponível' : 'Indisponível'}
                </span>
                {canChangeAvailability && <button
                  className="secondary-button compact-user-action"
                  disabled={mutation.isPending || !member.ativo}
                  onClick={() => mutation.mutate({ userId: member.usuario_id, data: { disponivel: !member.disponivel } })}
                >{member.disponivel ? 'Ficar indisponível' : 'Ficar disponível'}</button>}
              </div>
              <div className="team-attendant-capacity">
                <label className="field-label" htmlFor={`capacity-${member.usuario_id}`}>Limite de chamados ativos</label>
                {isAdmin ? <div className="team-capacity-control">
                  <input
                    id={`capacity-${member.usuario_id}`}
                    className="form-control"
                    type="number"
                    min="1"
                    step="1"
                    value={capacityDrafts[member.usuario_id] ?? String(member.capacidade_maxima)}
                    onChange={(event) => setCapacityDrafts((current) => ({ ...current, [member.usuario_id]: event.target.value }))}
                  />
                  <button className="secondary-button compact-user-action" disabled={mutation.isPending} onClick={() => saveCapacity(member.usuario_id, member.capacidade_maxima)} title="Salvar capacidade"><Save size={15}/> Salvar</button>
                </div> : <strong>{member.capacidade_maxima} chamados</strong>}
              </div>
            </article>
          })}
        </div>
      )}
    </section>

    <div className="workspace-notice"><ShieldCheck size={18}/><div><strong>Escopo atual: Suporte N1 e N2</strong><span>A disponibilidade e os limites são armazenados no backend. A distribuição automática e a carga real de chamados serão conectadas em uma etapa posterior. Infraestrutura permanece fora deste módulo.</span></div></div>
  </div>
}
