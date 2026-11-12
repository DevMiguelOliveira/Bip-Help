import { ArrowDown, Bot, CheckCircle2, ClipboardList, MessageCircle, Settings2, ShieldCheck } from 'lucide-react'

const steps = [
  { number: '01', title: 'Identificar o solicitante', description: 'Confirmar o usuário e a unidade vinculada à conta.', icon: ShieldCheck },
  { number: '02', title: 'Entender a solicitação', description: 'Perguntar se é um problema técnico, dúvida ou outra solicitação.', icon: MessageCircle },
  { number: '03', title: 'Coletar a descrição', description: 'Registrar o relato e permitir anexar imagens ou evidências.', icon: ClipboardList },
  { number: '04', title: 'Registrar e encaminhar', description: 'Criar o chamado e solicitar distribuição para a equipe de suporte.', icon: CheckCircle2 },
]

export default function BotPage() {
  return <div className="page-stack">
    <section className="welcome-row"><div><div className="eyebrow muted-eyebrow">AUTOMAÇÃO DE ATENDIMENTO</div><h1>BIP Bot</h1><p>Configure o roteiro de abertura e triagem dos chamados, sem inteligência artificial.</p></div><span className="workspace-status-pill"><span className="status-dot"/> Estrutura visual</span></section>
    <section className="bot-intro-card"><div className="bot-intro-icon"><Bot size={30}/></div><div><span className="section-kicker">ASSISTENTE DE ATENDIMENTO</span><h2>Triagem guiada, simples e padronizada</h2><p>O bot fará perguntas predefinidas, validará os dados da conta e registrará as respostas para que o suporte receba solicitações organizadas.</p></div></section>
    <section className="panel workspace-panel"><div className="panel-heading"><div><span className="section-kicker">ROTEIRO DE ATENDIMENTO</span><h2>Etapas do BIP Bot</h2><p>Fluxo proposto para a abertura de uma solicitação.</p></div><Settings2 className="heading-icon" size={20}/></div>
      <div className="bot-flow-list">{steps.map((step, index) => { const Icon = step.icon; return <div className="bot-flow-step" key={step.number}><div className="bot-flow-number">{step.number}</div><div className="bot-flow-icon"><Icon size={19}/></div><div className="bot-flow-copy"><strong>{step.title}</strong><span>{step.description}</span></div>{index < steps.length - 1 && <ArrowDown className="bot-flow-arrow" size={16}/>}</div> })}</div>
    </section>
    <div className="workspace-notice"><ShieldCheck size={18}/><div><strong>Fluxo visual em preparação</strong><span>As perguntas, validações, salvamento das respostas e abertura automática serão conectados ao backend na próxima etapa. Nenhum chamado é criado por esta tela ainda.</span></div></div>
  </div>
}
