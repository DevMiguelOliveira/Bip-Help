import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { UserPlus, Users, ShieldCheck, RefreshCw, X, UserRoundCheck, Link2 } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { createUser, getFranchises, getUsers, linkUserToFranchise } from '../services/data'
import type { User } from '../types'

export default function UsersPage() {
  const { token } = useAuth()
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [accountType, setAccountType] = useState('proprietario')
  const [franchiseId, setFranchiseId] = useState('')
  const [success, setSuccess] = useState('')
  const [linkingUser, setLinkingUser] = useState<User | null>(null)
  const [extraFranchiseId, setExtraFranchiseId] = useState('')
  const [extraRole, setExtraRole] = useState<'proprietario' | 'gerente' | 'funcionario'>('proprietario')
  const users = useQuery({ queryKey: ['users'], queryFn: () => getUsers(token!), enabled: !!token })
  const franchises = useQuery({ queryKey: ['franchises'], queryFn: () => getFranchises(token!), enabled: !!token })
  const linkMutation = useMutation({
    mutationFn: () => linkUserToFranchise(token!, linkingUser!.id, Number(extraFranchiseId), extraRole),
    onSuccess: async () => { setSuccess(`Unidade vinculada a ${linkingUser?.nome}.`); setLinkingUser(null); setExtraFranchiseId(''); await qc.invalidateQueries({ queryKey: ['users'] }) },
  })
  const mutation = useMutation({
    mutationFn: async () => {
      const profile = accountType === 'administrador' || accountType === 'suporte_n1' ? accountType : null
      const created = await createUser(token!, { nome: name, email, senha: password, perfil_sistema: profile })
      if (profile === null && franchiseId) await linkUserToFranchise(token!, created.id, Number(franchiseId), accountType as 'proprietario' | 'gerente' | 'funcionario')
      return created
    },
    onSuccess: async (created) => { setSuccess(`Usuário ${created.nome} cadastrado.`); setName(''); setEmail(''); setPassword(''); setShowForm(false); await qc.invalidateQueries({ queryKey: ['users'] }) },
  })
  return <div className="page-stack"><section className="welcome-row"><div><div className="eyebrow muted-eyebrow">ACESSOS E PERMISSÕES</div><h1>Usuários</h1><p>Gerencie contas individuais e acessos do BIPManager.</p></div><div className="welcome-actions"><button className="secondary-button" onClick={() => users.refetch()}><RefreshCw size={16} /> Atualizar</button><button className="primary-button" onClick={() => { setSuccess(''); setShowForm(true) }}><UserPlus size={17} /> Novo usuário</button></div></section>
    {success && <div className="success-banner"><ShieldCheck size={17} /> {success}</div>}
    <section className="user-summary-grid"><div className="mini-stat"><span className="mini-stat-icon blue"><Users size={17} /></span><div><strong>{users.data?.length || 0}</strong><small>Contas cadastradas</small></div></div><div className="mini-stat"><span className="mini-stat-icon green"><UserRoundCheck size={17} /></span><div><strong>{users.data?.filter((u) => u.ativo).length || 0}</strong><small>Contas ativas</small></div></div><div className="mini-stat"><span className="mini-stat-icon violet"><ShieldCheck size={17} /></span><div><strong>{users.data?.filter((u) => u.perfil_sistema).length || 0}</strong><small>Perfis de sistema</small></div></div></section>
    <section className="panel users-panel"><div className="panel-heading"><div><span className="section-kicker">CONTROLE DE ACESSO</span><h2>Contas do sistema</h2><p>As permissões por unidade são administradas pela API.</p></div></div>{users.isLoading ? <div className="loading-panel">Carregando usuários…</div> : <div className="user-list">{(users.data || []).map((u) => <div className="user-row" key={u.id}><div className="avatar user-row-avatar">{u.nome.split(/\s+/).slice(0, 2).map((x) => x[0]).join('').toUpperCase()}</div><div className="user-row-main"><strong>{u.nome}</strong><small>{u.email}</small></div><div className="user-role-cell">{u.perfil_sistema || 'Acesso por unidade'}</div><span className={`status-badge ${u.ativo ? 'status-green' : 'status-gray'}`}>{u.ativo ? 'Ativo' : 'Inativo'}</span>{!u.perfil_sistema && <button className="secondary-button compact-user-action" onClick={() => { setLinkingUser(u); setExtraFranchiseId(''); setExtraRole('proprietario') }}><Link2 size={14} /> Vincular unidade</button>}</div>)}</div>}</section>
    {showForm && <div className="modal-backdrop" onMouseDown={(e) => { if (e.target === e.currentTarget) setShowForm(false) }}><div className="modal-card"><div className="modal-heading"><div className="modal-icon"><UserPlus size={19} /></div><div><h2>Cadastrar usuário</h2><p>Crie uma conta individual para acesso à plataforma.</p></div><button className="icon-button modal-close" onClick={() => setShowForm(false)}><X size={18} /></button></div><form className="modal-form" onSubmit={(e) => { e.preventDefault(); mutation.mutate() }}><label className="field-label">Nome completo</label><input className="form-control" value={name} onChange={(e) => setName(e.target.value)} required minLength={2} maxLength={150} /><label className="field-label">E-mail</label><input className="form-control" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /><label className="field-label">Senha inicial</label><input className="form-control" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={14} maxLength={128} /><label className="field-label">Tipo de conta</label><select className="form-control" value={accountType} onChange={(e) => setAccountType(e.target.value)}><option value="proprietario">Proprietário</option><option value="gerente">Gerente</option><option value="funcionario">Funcionário</option><option value="suporte_n1">Suporte N1</option><option value="administrador">Administrador</option></select>{!['administrador', 'suporte_n1'].includes(accountType) && <><label className="field-label">Franquia inicial</label><select className="form-control" value={franchiseId} onChange={(e) => setFranchiseId(e.target.value)} required><option value="">Selecione uma unidade</option>{(franchises.data || []).map((f) => <option key={f.id} value={f.id}>{f.unidade}</option>)}</select></>} {mutation.isError && <div className="form-error">{mutation.error.message}</div>}<div className="modal-actions"><button type="button" className="secondary-button" onClick={() => setShowForm(false)}>Cancelar</button><button className="primary-button" disabled={mutation.isPending}>{mutation.isPending ? 'Salvando…' : 'Criar usuário'}</button></div></form></div></div>}
    {linkingUser && <div className="modal-backdrop" onMouseDown={(e) => { if (e.target === e.currentTarget) setLinkingUser(null) }}><div className="modal-card"><div className="modal-heading"><div className="modal-icon"><Link2 size={19} /></div><div><h2>Vincular outra unidade</h2><p>{linkingUser.nome} poderá acessar mais uma franquia.</p></div><button className="icon-button modal-close" onClick={() => setLinkingUser(null)}><X size={18} /></button></div><form className="modal-form" onSubmit={(e) => { e.preventDefault(); linkMutation.mutate() }}><label className="field-label">Unidade</label><select className="form-control" value={extraFranchiseId} onChange={(e) => setExtraFranchiseId(e.target.value)} required><option value="">Selecione uma unidade</option>{(franchises.data || []).map((f) => <option key={f.id} value={f.id}>{f.unidade}</option>)}</select><label className="field-label">Papel nesta unidade</label><select className="form-control" value={extraRole} onChange={(e) => setExtraRole(e.target.value as typeof extraRole)}><option value="proprietario">Proprietário</option><option value="gerente">Gerente</option><option value="funcionario">Funcionário</option></select>{linkMutation.isError && <div className="form-error">{linkMutation.error.message}</div>}<div className="modal-actions"><button type="button" className="secondary-button" onClick={() => setLinkingUser(null)}>Cancelar</button><button className="primary-button" disabled={linkMutation.isPending || !extraFranchiseId}>{linkMutation.isPending ? 'Vinculando…' : 'Confirmar vínculo'}</button></div></form></div></div>}
    </div>
}
