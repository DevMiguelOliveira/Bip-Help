import { BarChart3, Clock3, Gauge, TrendingUp } from 'lucide-react'

export default function PerformancePage() {
  return <div className="page-stack">
    <section className="welcome-row"><div><div className="eyebrow muted-eyebrow">INDICADORES OPERACIONAIS</div><h1>Desempenho</h1><p>Acompanhe a produtividade e o equilíbrio da operação de suporte.</p></div><span className="workspace-status-pill">Aguardando integração</span></section>
    <section className="performance-card-grid">
      <div className="performance-metric"><span><Gauge size={17}/> Carga por atendente</span><strong>—</strong><small>Será calculada pela carga ponderada.</small></div>
      <div className="performance-metric"><span><Clock3 size={17}/> Tempo de atendimento</span><strong>—</strong><small>Após integração dos registros.</small></div>
      <div className="performance-metric"><span><TrendingUp size={17}/> Chamados resolvidos</span><strong>—</strong><small>Por período e equipe.</small></div>
    </section>
    <section className="panel performance-placeholder"><BarChart3 size={28}/><h2>Indicadores de suporte</h2><p>Esta área receberá dados reais do BIPManager: volume de chamados, tempo de primeira resposta, tempo de resolução, reaberturas, transferências e distribuição da carga entre N1 e N2.</p></section>
  </div>
}
