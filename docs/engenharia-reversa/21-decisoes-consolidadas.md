# Decisões de Produto Consolidadas — Bip Help

Este documento consolida as cinco dúvidas de produto levantadas na auditoria Fase 5A (seção 11 — Dependentes de Produto) e as classifica em três categorias:

- **Decisão confirmada:** comportamento desejado pelo produto, com evidência ou definição clara.
- **Decisão pendente:** requer validação do produto antes de avançar para a Fase 5.
- **Fora do escopo:** não será implementado nesta versão.

Fonte: docs\engenharia-reversa\30-auditoria-fase5a.md (seção 11) e docs\engenharia-reversa\00-relatorio-final-fase4.md.

---

## 1. Serviços ausentes (chatAgents, chatIntegrator, ai, creditManagement, whatsapp)

**Classificação: Fora do escopo (versão atual)**

**Evidência:** A auditoria confirma que não há Axios, Socket.IO, objeto R nem estes serviços no repositório atual. O relatório Fase 4 também lista que chatAgents, chatIntegrator, ai, creditManagement e whatsapp não existem nesta versão.

**Comportamento atual:** Não há implementação, endpoint, bundle ou referência funcional a estes serviços no frontend ou backend.

**Decisão:** Não serão implementados nesta versão. Caso o produto queira esses serviços no futuro, devem ser planejados em outra fase ou repositório separado (BIPManager ≠ BIPRemote).

**Impacto na Fase 5:** Nenhum. A Fase 5 foca nos serviços presentes (tickets, mensagens, equipe, franquias, usuários, autenticação, WebSocket nativo).

---

## 2. Objeto R / getAPIURL / R.services

**Classificação: Fora do escopo (versão atual)**

**Evidência:** Nenhum arquivo do frontend ou backend contém `R.url.getAPIURL`, `R.services` ou inicialização de um objeto `R`. A auditoria Fase 5A confirma a ausência destes artefatos.

**Comportamento atual:** O frontend resolve a URL da API via `VITE_API_URL` com fallback para mesma origem (`frontend/src/lib/api.ts:2–4`). Não há registro central de serviços `R.services`.

**Decisão:** Não será implementado nesta versão. A resolução de URLs segue o padrão existente (variável de ambiente + fallback). Se o objeto R for necessário, deve ser especificado pelo produto em uma versão futura.

**Impacto na Fase 5:** Nenhum. Mantém-se a arquitetura de resolução de URL atual.

---

## 3. Timeout de 15 segundos

**Classificação: Decisão pendente**

**Evidência:** Não há implementação de timeout de 15s no código do repositório (nem no backend FastAPI, nem no frontend Axios/fetch, nem em configuração de proxy/Nginx presente no repo). A dúvida é se esse timeout é de responsabilidade da infraestrutura (Nginx, balanceador).

**Pergunta ao produto:** O timeout de 15s é um requisito de infraestrutura a ser configurado fora do repositório, ou deve ser implementado no cliente HTTP/backend? Qual o comportamento desejado quando excedido?

**Decisão:** Pendente validação do produto.

**Impacto na Fase 5:** Afeta a definição de resiliência do cliente HTTP e eventuais ajustes de proxy. Não bloqueia o diagnóstico, mas deve ser decidido antes de implementar tratativas de timeout.

---

## 4. Capacidade de atendente (capacidade_maxima / disponivel)

**Classificação: Decisão pendente**

**Evidência:** `AtendenteConfig` armazena `capacidade_maxima` e `disponivel` (`backend/models.py:133–143`), mas estes campos não são usados para distribuição ou atribuição de tickets (`backend/main.py:446–481`). A configuração é apenas exibição (`GET /equipe/`).

**Pergunta ao produto:** A capacidade do atendente deve limitar e direcionar a distribuição automática de tickets, ou permanece como indicador apenas de exibição?

**Decisão:** Pendente validação do produto.

**Impacto na Fase 5:** Se for desejado afetar distribuição, a Fase 5 deve incluir lógica de roteamento automático e validação de capacidade. Se for apenas exibição, nenhuma mudança é necessária.

---

## 5. Endpoints de edição/exclusão de mensagem e consulta individual de ticket

**Classificação: Decisão pendente**

**Evidência:**
- Não existe `GET /tickets/{id}` (consulta individual) — auditoria Fase 5A, item 5.4.
- Não existem `PUT`/`DELETE` para mensagens — auditoria Fase 5A, item 5.3.
- Mensagens são imutáveis após criação (`backend/main.py` não tem endpoint de edição/exclusão).

**Pergunta ao produto:** Esses endpoints são necessários para o fluxo operacional de chamados e mensagens (edição de erros, consulta detalhada do ticket)?

**Decisão:** Pendente validação do produto.

**Impacto na Fase 5:** Se confirmado como necessário, a Fase 5 deve implementar `GET /tickets/{id}`, edição e exclusão de mensagens com regras de permissão e integridade. Caso contrário, permanecem como não implementados.

---

## Resumo das classificações

| Item | Classificação | Motivo |
|------|--------------|--------|
| Serviços ausentes | Fora do escopo | Não existem neste repositório nesta versão |
| Objeto R / getAPIURL / R.services | Fora do escopo | Não existem; padrão atual de URL se mantém |
| Timeout de 15s | Decisão pendente | Precisa validação de infraestrutura/produto |
| Capacidade de atendente | Decisão pendente | Precisa definição se afeta distribuição ou é exibição |
| Edição/exclusão de mensagem e consulta individual | Decisão pendente | Precisa validação de necessidade no fluxo operacional |

---

## Próximo passo para a Fase 5

Aguardar as decisões do produto sobre os três itens pendentes antes de iniciar o diagnóstico técnico com prioridades e critérios de aceitação. Os dois itens fora do escopo já estão descartados desta versão.

Restrição respeitada: nenhum código, migration, banco ou configuração foi alterado. Este documento é exclusivamente de decisões de produto.
