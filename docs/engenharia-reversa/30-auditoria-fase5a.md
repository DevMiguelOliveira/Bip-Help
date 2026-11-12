# Relatório de Auditoria Técnica e Funcional — Fase 5A — Bip Help

**Projeto:** Bip Help  
**Workspace:** D:\PROJETOS\BipHelp  
**Tipo:** Auditoria somente leitura — sem alterações de código, banco ou configurações  
**Base:** Documentos das Fases 1–4 e código-fonte atual do repositório  

---

## 1. Resumo Executivo

O Bip Help é um sistema de atendimento por tickets com backend FastAPI (porta 8001) e frontend React+Vite+TanStack Query. A auditoria confirma a arquitetura documentada na Fase 4 e identifica riscos técnicos, divergências frontend×backend, fragilidades de autorização, problemas de integridade de dados e débitos técnicos.

Não há Axios, Socket.IO, objeto R nem serviços chatAgents, chatIntegrator, ai, creditManagement ou whatsapp nesta versão.

---

## 2. Escopo e Metodologia

- Leitura completa de backend/main.py, backend/auth.py, backend/models.py, backend/schemas.py, backend/database.py.
- Leitura de frontend/src/lib/api.ts, frontend/src/services/data.ts, frontend/src/services/auth.ts, frontend/src/context/AuthContext.tsx.
- Verificação de linhas de código com Select-String e leitura direta de arquivos.
- Classificação de cada conclusão conforme: Confirmado, Provável, Não identificado, Divergente, Dependente de produto.
- Nenhuma operação de escrita executada contra código ou banco de dados.

---

## 3. Riscos Técnicos Confirmados

### 3.1 Segredo JWT exposto em caminho absoluto de arquivo

**Arquivo:** backend/auth.py:22–26  
**Comportamento:** O segredo JWT é lido de /etc/bipmanager/jwt_secret em tempo de importação do módulo. Se o arquivo não existir ou tiver menos de 64 caracteres, a aplicação levanta RuntimeError e não inicia.  
**Impacto:** O segredo é um ponto único de falha. O arquivo está fora do repositório e não está versionado, dificultando rotação e deploy em ambientes diferentes.  
**Classificação:** Confirmado

### 3.2 Token WebSocket expira em 60 segundos sem renovação automática

**Arquivo:** backend/auth.py:281, backend/main.py:1166  
**Comportamento:** WEBSOCKET_TOKEN_EXPIRE_SECONDS = 60. O endpoint POST /tickets/{ticket_id}/ws-token retorna expires_in: 60. O frontend não implementa renovação proativa do token.  
**Impacto:** Conexões WebSocket podem cair silenciosamente após 1 minuto, exigindo handshake manual pelo usuário.  
**Classificação:** Confirmado

### 3.3 Validação de acesso WebSocket ocorre apenas no handshake

**Arquivo:** backend/main.py:1175–1286  
**Comportamento:** O WebSocket validar verificar_acesso_ticket somente no momento da conexão. Após o handshake, não há revalidação de acesso ao ticket durante a sessão.  
**Impacto:** Se o acesso ao ticket for revogado durante uma sessão WS ativa (ex: vínculo desativado), o usuário continua recebendo eventos.  
**Classificação:** Confirmado

### 3.4 Upload de arquivo lido inteiro em memória antes de validação de tamanho

**Arquivo:** backend/main.py:947–950  
**Comportamento:** await file.read(MAX_UPLOAD_BYTES + 1) carrega todo o conteúdo em memória antes de checar len(conteudo) > MAX_UPLOAD_BYTES.  
**Impacto:** Possível exaustão de memória com uploads muito grandes.  
**Classificação:** Confirmado

### 3.5 Ausência de índice em Ticket.franquia_id para filtros frequentes

**Arquivo:** backend/models.py:42  
**Comportamento:** franquia_id = Column(Integer, ForeignKey("franquias.id")) sem index=True.  
**Impacto:** Consultas GET /tickets/ filtram por franquia_id em escala crescente; sem índice, desempenho degrada com volume.  
**Classificação:** Confirmado

---

## 4. Inconsistências entre Frontend e Backend (Divergentes)

### 4.1 Filtro de status de ticket ignorado pelo frontend

**Arquivo frontend:** frontend/src/services/data.ts:13–20  
**Arquivo backend:** backend/main.py:785–796  
**Comportamento:** O frontend recebe parâmetro status em getTickets() mas o descarta (void status). O backend não expõe parâmetro de filtro por status.  
**Impacto:** O usuário não pode filtrar tickets por status via interface nem via API.  
**Classificação:** Divergente

### 4.2 Controle de status no chat limitado no frontend

**Arquivo frontend:** TicketChatDialog.tsx (referenciado no relatório Fase 4)  
**Arquivo backend:** backend/main.py:824–866  
**Comportamento:** O frontend exibe select de status apenas para administrador e suporte_n1. O backend permite suporte_n2 alterar status.  
**Impacto:** suporte_n2 não pode alterar status via interface, embora tenha permissão na API.  
**Classificação:** Divergente

### 4.3 Autenticação delegada ao backend sem validação prévia no frontend

**Arquivo frontend:** frontend/src/lib/api.ts:36–38  
**Arquivo backend:** backend/main.py (todos os endpoints protegidos por Depends(get_current_user))  
**Comportamento:** O frontend não impõe regras próprias de autorização; depende exclusivamente de respostas 401/403 do backend.  
**Impacto:** Comportamento divergente entre camadas; falhas de autorização só são detectadas no servidor.  
**Classificação:** Divergente

---

## 5. Fragilidades nas Regras de Negócio

### 5.1 Sem validação de transição de status de ticket

**Arquivo:** backend/main.py:824–866  
**Comportamento:** PATCH /tickets/{id} permite definir qualquer status para qualquer ticket (ex: de Encerrado para Aberto).  
**Impacto:** Não há controle de fluxo de estados.  
**Classificação:** Confirmado

### 5.2 Sem identificação de criador de ticket

**Arquivo:** backend/models.py:39–46, backend/main.py:734–753  
**Comportamento:** O modelo Ticket não possui campo de usuário criador. criar_ticket não registra quem abriu o chamado.  
**Impacto:** Impossível auditar autoria de tickets.  
**Classificação:** Confirmado

### 5.3 Sem edição nem exclusão de mensagens

**Arquivo:** backend/main.py (nenhum endpoint PUT/DELETE para mensagens)  
**Comportamento:** Mensagens são imutáveis após criação.  
**Impacto:** Não há como corrigir erros em mensagens enviadas.  
**Classificação:** Confirmado

### 5.4 Sem consulta individual de ticket (GET /tickets/{id})

**Arquivo:** backend/main.py (apenas GET /tickets/ e PATCH /tickets/{id})  
**Comportamento:** Não existe endpoint para obter um único ticket por ID.  
**Impacto:** O frontend não pode carregar detalhes de um ticket específico sem listar todos.  
**Classificação:** Confirmado

### 5.5 Capacidade de atendente sem efeito operacional

**Arquivo:** backend/models.py:133–143, backend/main.py:446–481  
**Comportamento:** capacidade_maxima e disponivel são armazenados em AtendenteConfig mas não usados para distribuição ou atribuição de tickets.  
**Impacto:** Configuração de equipe é apenas exibição; não afeta o fluxo de atendimento.  
**Classificação:** Confirmado

### 5.6 Sem distribuição automática de tickets

**Arquivo:** backend/main.py (nenhuma lógica de atribuição)  
**Comportamento:** Tickets são criados sem atribuição a atendentes.  
**Impacto:** Não há roteamento automático para a equipe de suporte.  
**Classificação:** Confirmado

---

## 6. Problemas de Segurança e Autorização

### 6.1 Token JWT armazenado em localStorage no frontend

**Arquivo:** frontend/src/context/AuthContext.tsx:15, frontend/src/services/auth.ts  
**Comportamento:** Token é persistido em localStorage (chave bip-access-token). Não há uso de cookies HttpOnly.  
**Impacto:** Vulnerável a roubo via XSS.  
**Classificação:** Confirmado

### 6.2 Endpoint /uploads/{filename} valida acesso ao ticket mas não restringe por papel do remetente da mensagem interna

**Arquivo:** backend/main.py:1064–1134  
**Comportamento:** O download de anexo consulta a mensagem por url_anexo e verifica verificar_acesso_ticket. Usuários de franquia com acesso ao ticket podem baixar anexos de mensagens internas?  
**Análise:** O endpoint obter_anexo não filtra por interna == False para não-suporte. Se um usuário de franquia tem acesso ao ticket, ele pode baixar qualquer anexo vinculado a esse ticket, incluindo anexos de mensagens internas criadas por suporte.  
**Impacto:** Possível vazamento de conteúdo interno para não-suporte.  
**Classificação:** Provável (requer confirmação de cenário específico)

### 6.3 WebSocket valida Origin contra lista estática

**Arquivo:** backend/main.py:1183–1187  
**Comportamento:** FRONTEND_ORIGINS é uma lista fixa com https://bip-manager.lovable.app, http://127.0.0.1:5173, http://localhost:5173.  
**Impacto:** Produção fora dessa lista não conseguirá conectar via WebSocket sem alteração de código.  
**Classificação:** Confirmado

### 6.4 Senha hash dummy para mitigação de timing attack

**Arquivo:** backend/auth.py:45–56, backend/auth.py:88–89  
**Comportamento:** Quando o usuário não existe, verify_password é executado com DUMMY_HASH para equalizar tempo de resposta.  
**Impacto:** Boa prática de segurança implementada.  
**Classificação:** Confirmado (controle positivo)

---

## 7. Problemas de Integridade e Consistência de Dados

### 7.1 Soft delete de vínculo usuário-franquia não desativa tickets ou mensagens

**Arquivo:** backend/main.py:617–632  
**Comportamento:** DELETE /usuarios/{id}/franquias/{fid} define ativo = false no vínculo, mas tickets e mensagens associados permanecem inalterados.  
**Impacto:** Dados órfãos ou inconsistentes podem permanecer acessíveis.  
**Classificação:** Confirmado

### 7.2 Telefone único em franquia pode bloquear recriação após exclusão lógica

**Arquivo:** backend/models.py:23, backend/main.py:714–717  
**Comportamento:** telefone = Column(String, unique=True). Não há endpoint para reativar franquia inativa com mesmo telefone.  
**Impacto:** Se uma franquia for desativada (soft delete futuro) e recriada com mesmo telefone, haverá conflito de integridade.  
**Classificação:** Provável

### 7.3 AtendenteConfig pode existir para usuário não suporte

**Arquivo:** backend/main.py:364–374 (criação condicional apenas para suporte_n1/n2), backend/main.py:446–481 (atualização permite qualquer usuario_id)  
**Comportamento:** Na criação, AtendenteConfig só é criada para suporte_n1/suporte_n2. Na atualização via PATCH /equipe/{id}, não há verificação de que o usuário seja suporte antes de criar/configurar AtendenteConfig (apenas verifica usuario.perfil_sistema in ("suporte_n1", "suporte_n2") no final, mas o config pode ser criado antes para qualquer usuário).  
**Impacto:** Possível criação de configuração de atendente para usuário não suporte.  
**Classificação:** Provável

---

## 8. Débitos Técnicos Relevantes

### 8.1 Arquivos de backup e scripts de correção espalhados no repositório

**Arquivos:** backend/main_backup_*.py, backend/fix_*.py, backend/update_*.py, frontend/vite.config.ts.bak_*  
**Comportamento:** Múltiplos arquivos de backup e scripts de correção permanecem no repositório.  
**Impacto:** Ruído no versionamento, risco de execução acidental, confusão de manutenção.  
**Classificação:** Confirmado

### 8.2 URL do banco e segredo JWT fora do repositório

**Arquivo:** backend/database.py:8, backend/auth.py:22  
**Comportamento:** Ambas as configurações são lidas de arquivos absolutos (/etc/bipmanager/database_url, /etc/bipmanager/jwt_secret).  
**Impacto:** Dificulta deploy em ambientes sem esses arquivos pré-configurados. Não há fallback ou variável de ambiente.  
**Classificação:** Confirmado

### 8.3 Sem paginação configurável além de limite fixo de 500

**Arquivo:** frontend/src/services/data.ts:13, 15 (limit=500), backend/main.py:780–781 (skip, limit default 100/500)  
**Comportamento:** O frontend sempre solicita limit=500.  
**Impacto:** Com volume crescente de dados, a listagem pode se tornar lenta.  
**Classificação:** Provável

---

## 9. Dependências e Pontos de Acoplamento

### 9.1 Acoplamento forte entre backend e frontend por caminho absoluto

**Arquivo:** backend/database.py:8, backend/auth.py:22  
**Comportamento:** Ambas as dependências críticas apontam para caminhos absolutos no sistema de arquivos do servidor.  
**Impacto:** O sistema não é portável sem provisionamento prévio desses arquivos.  
**Classificação:** Confirmado

### 9.2 Frontend depende de VITE_API_URL para base URL

**Arquivo:** frontend/src/lib/api.ts:2–4  
**Comportamento:** API_BASE é lido de import.meta.env.VITE_API_URL, fallback para string vazia.  
**Impacto:** Se não definido, requisições são feitas para a mesma origem, o que pode falhar em deploy separado.  
**Classificação:** Confirmado

### 9.3 WebSocket acoplado a endpoint REST de emissão de token

**Arquivo:** backend/main.py:1141–1167, TicketChatDialog.tsx (frontend)  
**Comportamento:** O frontend deve chamar POST /tickets/{id}/ws-token antes de abrir o WebSocket.  
**Impacto:** Duas chamadas sequenciais obrigatórias para comunicação em tempo real.  
**Classificação:** Confirmado (arquitetural, não defeito)

---

## 10. Funcionalidades Partialmente Implementadas

| Funcionalidade | Estado | Evidência |
|---|---|---|
| Filtro de status na listagem de tickets | Parcial | frontend/src/services/data.ts:17 (void status); backend não expõe parâmetro |
| Controle de status no chat | Parcial | Frontend limita a admin/suporte_n1; backend permite suporte_n2 (main.py:824–866) |
| Capacidade de atendente | Parcial | capacidade_maxima e disponivel armazenados mas não usados (models.py:133–143) |
| Expiração de token WS | Parcial | 60s sem renovação automática (auth.py:281, main.py:1166) |
| Acesso ao ticket durante WS | Parcial | Validação só no handshake (main.py:1175–1286) |

---

## 11. Dependentes de Produto (Decisão necessária)

| Item | Pergunta ao produto | Classificação |
|---|---|---|
| Serviços ausentes (chatAgents, chatIntegrator, ai, creditManagement, whatsapp) | Planejados para outra fase ou outro repositório? | Dependente de produto |
| Objeto R / getAPIURL / R.services | Existem em versão anterior ou branch diferente? | Dependente de produto |
| Timeout de 15s | Implementado na infraestrutura (Nginx, balanceador)? | Dependente de produto |
| Capacidade de atendente | Deve afetar distribuição de tickets ou é apenas exibição? | Dependente de produto |
| Endpoints de edição/exclusão de mensagem e consulta individual de ticket | Necessários para o fluxo operacional? | Dependente de produto |

---

## 12. Conclusão e Recomendações para a Fase 5

A auditoria confirma que o Bip Help possui uma base funcional sólida para atendimento por tickets, com autenticação JWT, CRUD de usuários/franquias/tickets/mensagens, WebSocket nativo e controle de permissões por papel. No entanto, apresenta:

1. Riscos críticos: segredo JWT em caminho absoluto, token WS de curta duração sem renovação, validação de acesso WS apenas no handshake, upload em memória.
2. Regras de negócio incompletas: sem transição de status, sem criador de ticket, sem edição/exclusão de mensagem, sem consulta individual, sem distribuição automática.
3. Divergências frontend×backend: filtro de status, controle de status no chat, autorização delegada.

**Recomendações para a Fase 5 (não implementar nesta fase):**
- Priorizar correções de segurança (JWT, WS, upload).
- Definir com o produto os itens dependentes (seção 11).
- Planejar regras de transição de status e distribuição de tickets.
- Remover arquivos de backup e scripts de correção do repositório.

---

**Restrições respeitadas:** Nenhum código, migration, banco ou configuração foi alterado. Esta fase é exclusivamente de auditoria e documentação.
