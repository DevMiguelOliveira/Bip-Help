# Decisões de Produto — BIPManager

Este documento registra as decisões estratégicas de produto para o BIPManager, servindo de base para a Fase 5.

## 1. Decisões Confirmadas
- *Nenhuma decisão confirmada nesta fase.*

## 2. Decisões Pendentes (Validação necessária)
| Item | Descrição | Impacto |
|---|---|---|
| **Serviços Ausentes** | Status dos serviços chatAgents, chatIntegrator, i, creditManagement e whatsapp. Planejados? | Arquitetura |
| **Objeto R** | A existência de R / getAPIURL / R.services é necessária ou obsoleta? | Frontend |
| **Timeout de 15s** | O timeout de 15s está implementado na infraestrutura? | Comunicação |
| **Capacidade de Atendente** | Deve limitar/distribuir tickets ou apenas exibição? | Regra de Negócio |
| **Endpoits de Mensagens/Tickets** | É necessário implementar edição/exclusão de mensagem e consulta individual de ticket? | CRUD/API |

## 3. Fora do Escopo (Versão atual)
- A implementação dos serviços ausentes (chatAgents, etc) não faz parte deste repositório nesta versão.
- Refatoração de infraestrutura para timeout não será realizada nesta fase.
