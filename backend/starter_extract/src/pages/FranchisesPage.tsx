import { useQuery } from '@tanstack/react-query'
import { Building2, MapPin, Phone, RefreshCw, Store } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { getFranchises } from '../services/data'

export default function FranchisesPage() {
  const { token, user } = useAuth()
  const { data = [], isLoading, refetch } = useQuery({ queryKey: ['franchises'], queryFn: () => getFranchises(token!), enabled: !!token })
  return <div className="page-stack"><section className="welcome-row"><div><div className="eyebrow muted-eyebrow">REDE DE OPERAÇÕES</div><h1>Franquias</h1><p>Unidades disponíveis no escopo de acesso da sua conta.</p></div><button className="secondary-button" onClick={() => refetch()}><RefreshCw size={16} /> Atualizar</button></section><div className="franchise-grid">{isLoading ? <div className="panel loading-panel">Carregando unidades…</div> : data.map((f) => { const role = user?.franquias.find((x) => x.franquia_id === f.id)?.papel; return <article className="franchise-card" key={f.id}><div className="franchise-card-top"><div className="franchise-icon"><Store size={20} /></div><span className={`status-badge ${f.ativa ? 'status-green' : 'status-gray'}`}>{f.ativa ? 'Ativa' : 'Inativa'}</span></div><h3>{f.unidade}</h3><p className="franchise-manager">{f.nome_responsavel}</p><div className="franchise-meta"><span><Phone size={14} /> {f.telefone}</span><span><MapPin size={14} /> Unidade #{f.id}</span></div>{role && <div className="franchise-role"><span>Seu acesso</span><strong>{role}</strong></div>}</article> })}{!isLoading && !data.length && <div className="panel empty-state"><Building2 size={22} /><strong>Nenhuma franquia disponível</strong><p>Não há unidades vinculadas à sua conta.</p></div>}</div></div>
}
