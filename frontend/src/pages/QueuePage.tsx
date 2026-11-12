import { Clock3, Inbox, Bell, ShieldCheck } from 'lucide-react'

export default function QueuePage() {
  return <div className="page-stack">
    <section className="welcome-row"><div><div className="eyebrow muted-eyebrow">DISTRIBUIÇÃO DE ATENDIMENTO</div><h1>Fila de espera</h1><p>Chamados aguardando disponibilidade de um atendente do Suporte N1 ou N2.</p></div><span className="workspace-status-pill"><Clock3 size={14}/> Em preparação</span></section>
    <section className="queue-summary-grid"><div className="queue-summary-card"><span>Na fila</span><strong>—</strong><small>Aguardando integração</small></div><div className="queue-summary-card"><span>Maior tempo de espera</span><strong>—</strong><small>Sem dados conectados</small></div><div className="queue-summary-card"><span>Supervisores notificados</span><strong>—</strong><small>Notificações ainda não integradas</small></div></section>
    <section className="panel queue-empty-panel"><div className="queue-empty-icon"><Inbox size={26}/></div><h2>A fila será exibida aqui</h2><p>Quando a distribuição automática estiver integrada, os chamados sem atendente disponível aparecerão nesta tela, ordenados por prioridade e tempo de espera.</p><div className="queue-rule-chips"><span><Clock3 size={14}/> Ordem por prioridade e espera</span><span><Bell size={14}/> Aviso ao supervisor</span><span><ShieldCheck size={14}/> Histórico de movimentações</span></div></section>
  </div>
}
