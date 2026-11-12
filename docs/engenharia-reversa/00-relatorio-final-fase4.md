# Relatório Final Consolidado — Fase 4: Regras de Negócio e Fluxos Operacionais do BIPManager

**Base:** D:\PROJETOS\BipHelp
**Shell:** PowerShell
**Restrição respeitada:** Nenhum código, migration, banco ou configuração foi alterado.
**Status:** Consolidado a partir dos 7 documentos da Fase 4 (docs\engenharia-reversa\10- a 16-*). Nenhuma funcionalidade foi inventada; itens sem evidência são marcados como não identificados.

---

## 1. Resumo Executivo

O BIPManager é um sistema de atendimento por tickets com backend FastAPI (porta 8001) e frontend React+Vite+TanStack Query. A arquitetura de comunicação foi mapeada integralmente: autenticação JWT, CRUD de usuários/franquias/tickets/mensagens, WebSocket nativo para tempo real, upload de anexos e gestão de equipe de suporte. Não há Axios, Socket.IO, objeto R nem os serviços chatAgents, chatIntegrator, ai, creditManagement e whatsapp nesta versão do repositório. Sete documentos de engenharia reversa foram produzidos (10 a 16) e este relatório consolida seu conteúdo.

---

## 2. Regras de Negócio Confirmadas

Todas as regras abaixo possuem evidência de linha no código-fonte.

### 2.1 Identidade, autenticação e autorização

| # | Regra | Evidência |
|---|-------|-----------|
| 2.1.1 | POST /auth/login recebe OAuth2 form (username = e-mail, password). Retorna 401 com WWW-Authenticate: Bearer em falha. | backend/main.py:260-282 |
| 2.1.2 | E-mail normalizado com strip().lower() antes de consultar o usuário. | backend/auth.py:80-97 |
| 2.1.3 | Se usuário não existir, verify_password é executado com hash dummy para mitigar timing attack. | backend/auth.py:88-89 |
| 2.1.4 | Usuário inativo (ativo = false) é rejeitado no login e na validação de token. | backend/auth.py:102, 192 |
| 2.1.5 | Token JWT emitido com create_access_token(user.id), expiração 30 min, token_use=access. | backend/auth.py:36, 110-111 |
| 2.1.6 | Segredo JWT lido de /etc/bipmanager/jwt_secret, mínimo 64 caracteres, algoritmo HS256. | backend/auth.py:22, 24-26 |
| 2.1.7 | Frontend armazena token em localStorage (chave bip-access-token). Não há uso de cookies. | temp_restore/frontend/src/context/AuthContext.tsx:15 |
| 2.1.8 | get_current_user decodifica JWT exigindo exp, iat, sub, iss, aud e verificando token_use == "access". | backend/auth.py:149-161 |
| 2.1.9 | GET /auth/me retorna dados do usuário + lista de franquias ativas vinculadas. | backend/main.py:291-324 |

### 2.2 Perfis e papéis

| # | Regra | Evidência |
|---|-------|-----------|
| 2.2.1 | perfil_sistema: administrador, suporte_n1, suporte_n2, NULL (check constraint ck_usuarios_perfil_sistema). | backend/models.py:91-93 |
| 2.2.2 | papel de franquia: proprietario, gerente, funcionario (check constraint ck_usuario_franquias_papel). | backend/models.py:176-181 |
| 2.2.3 | Usuários administrativos (perfil_sistema não nulo) não recebem papel por franquia. | backend/main.py:575-577 |

### 2.3 Franquias

| # | Regra | Evidência |
|---|-------|-----------|
| 2.3.1 | POST /franquias/ cria franquia (apenas administrador). Campos: nome_responsavel, unidade, telefone. | backend/main.py:696-717 |
| 2.3.2 | Telefone é único; conflito retorna HTTP 409. | backend/models.py:23, main.py:714-717 |
| 2.3.3 | GET /franquias/ lista franquias. Não-administrativos veem apenas vinculadas e ativas. | backend/main.py:657-678 |
| 2.3.4 | Não há endpoint para ativar/desativar franquia. | Não encontrado |

### 2.4 Tickets

| # | Regra | Evidência |
|---|-------|-----------|
| 2.4.1 | POST /tickets/ cria ticket com franquia_id e descricao (1-10000 chars). Status padrão "Aberto". | backend/main.py:734-753 |
| 2.4.2 | Não há campo de usuário criador no modelo de ticket. | backend/models.py:39-46 |
| 2.4.3 | GET /tickets/ filtra por franquia autorizada se usuário não for administrador/suporte. Ordena por criado_em.desc(), id.desc(). | backend/main.py:764-807 |
| 2.4.4 | PATCH /tickets/{id}: suporte pode alterar status e descricao; proprietario/gerente só descricao e apenas se status == "Aberto"; funcionario recebe 403. | backend/main.py:824-866 |
| 2.4.5 | Não há validação de transição de status (qualquer status pode ser definido para qualquer ticket). | backend/main.py:824-866 |
| 2.4.6 | Não há endpoint GET /tickets/{id} (consulta individual). | Não encontrado |

### 2.5 Mensagens

| # | Regra | Evidência |
|---|-------|-----------|
| 2.5.1 | POST /tickets/{id}/mensagens/ aceita FormData (texto, file, interna). | backend/main.py:898-988 |
| 2.5.2 | interna == true requer que o usuário seja suporte (caso contrário 403). | backend/main.py:928-932 |
| 2.5.3 | Anexo máximo 20 MB, tipos JPG/PNG/WEBP detectados por assinatura binária. Armazenado em backend/uploads/. | backend/main.py:98-101, 947-950 |
| 2.5.4 | Não há edição nem exclusão de mensagens. | Não encontrado |

### 2.6 Equipe de suporte

| # | Regra | Evidência |
|---|-------|-----------|
| 2.6.1 | GET /equipe/ lista atendentes (suporte_n1/suporte_n2) com disponibilidade e capacidade. | backend/main.py:408-481 |
| 2.6.2 | PATCH /equipe/{id}: administrador pode alterar qualquer atendente (incluindo capacidade_maxima); atendente altera apenas disponível de si mesmo. | backend/main.py:408-481 |
| 2.6.3 | capacidade_maxima e disponivel são armazenados mas não usados para distribuição automática de tickets. | Não encontrado |

---

## 3. Matriz de Permissões

| Endpoint | Método | Perfil permitido | Papel franquia permitido | Confiança | Evidência |
|----------|--------|------------------|--------------------------|-----------|-----------|
| / | GET | Público | Nenhum | confirmado | main.py:247 |
| /auth/login | POST | Público | Nenhum | confirmado | main.py:259 |
| /auth/me | GET | Qualquer autenticado ativo | Qualquer | confirmado | main.py:291 |
| /usuarios/ | POST | administrador | Nenhum | confirmado | main.py:339 |
| /usuarios/ | GET | administrador | Nenhum | confirmado | main.py:382 |
| /usuarios/{id}/franquias | POST | administrador | Nenhum | confirmado | main.py:534 |
| /usuarios/{id}/franquias/{fid} | DELETE | administrador | Nenhum | confirmado | main.py:617 |
| /franquias/ | GET | Qualquer autenticado | Vínculo ativo (se não-admin) | confirmado | main.py:657 |
| /franquias/ | POST | administrador | Nenhum | confirmado | main.py:696 |
| /tickets/ | POST | Qualquer autenticado | Qualquer papel na franquia | confirmado | main.py:734 |
| /tickets/ | GET | Qualquer autenticado | Vínculo ativo (se não-admin) | confirmado | main.py:764 |
| /tickets/{id} | PATCH | Qualquer autenticado | proprietario/gerente (descricao); suporte (status+descricao) | confirmado | main.py:824 |
| /tickets/{id}/mensagens/ | POST | Qualquer autenticado | Qualquer papel; interna só suporte | confirmado | main.py:898 |
| /tickets/{id}/mensagens/ | GET | Qualquer autenticado | Qualquer papel; não-suporte não vê internas | confirmado | main.py:1011 |
| /uploads/{filename} | GET | Qualquer autenticado | Acesso ao ticket da mensagem | confirmado | main.py:1064 |
| /tickets/{id}/ws-token | POST | Qualquer autenticado | Qualquer papel na franquia | confirmado | main.py:1140 |
| WS /ws/tickets/{id} | WS | Token válido + acesso ao ticket | Qualquer papel; is_support filtra internas | confirmado | main.py:1175 |

### Diferenças frontend × backend

| Aspecto | Frontend | Backend | Status |
|---------|----------|---------|--------|
| Controle de status do ticket | Select apenas administrador e suporte_n1 | PATCH permite suporte_n2 também | Divergência parcial |
| Filtro de status na listagem | Parâmetro recebido, ignorado (void status) | Parâmetro não exposto | Divergência |
| Autorização | Não impõe regras próprias; depende de 401/403 | Aplica todas via Depends | Comportamento divergente |

---

## 4. Fluxos Operacionais Reconstruídos

### Fluxo 1 — Autenticação
1. Usuário acessa tela de login (LoginPage.tsx).
2. Frontend envia POST /auth/login (form-urlencoded).
3. Backend normaliza e-mail, consulta usuário, verifica senha com timing-attack mitigation.
4. Emite JWT (30 min). Frontend armazena em localStorage.
5. Frontend chama GET /auth/me.
6. 401 dispara logout (remove localStorage).
**Evidências:** auth.py:65-123, main.py:259-324, services/auth.ts, AuthContext.tsx, lib/api.ts.

### Fluxo 2 — Criação de ticket
1. Usuário preenche franquia_id e descricao.
2. POST /tickets/ com { franquia_id, descricao }.
3. Backend verifica franquia ativa e papel na franquia.
4. Cria ticket com status "Aberto". Retorna TicketResponse.
**Evidências:** main.py:734-753, models.py:58-66, data.ts:23-26.

### Fluxo 3 — Listagem de tickets
1. GET /tickets/?limit=500 [?franquia_id=N].
2. Backend filtra por franquia autorizada se não-admin.
3. Ordena por criado_em.desc(), id.desc(). Paginação skip/limit.
**Evidências:** main.py:764-807, data.ts:13-20.

### Fluxo 4 — Alteração de ticket (PATCH)
1. PATCH /tickets/{id} com { status?, descricao? }.
2. Valida acesso ao ticket.
3. Não-suporte: proprietario/gerente edita apenas descricao, só se "Aberto", não altera status.
4. Suporte: altera status e descricao. Faz broadcast ticket_updated via WS.
**Evidências:** main.py:824-866.

### Fluxo 5 — Envio de mensagem
1. POST /tickets/{id}/mensagens/ com FormData (texto, file, interna).
2. Valida acesso. interna requer suporte.
3. Anexo: ≤20 MB, detecção JPG/PNG/WEBP, salva em backend/uploads/.
4. Cria mensagem, faz broadcast new_message (pula internas para não-suporte).
**Evidências:** main.py:898-988, models.py:97-109.

### Fluxo 6 — Listagem de mensagens
1. GET /tickets/{id}/mensagens/.
2. Não-suporte: filtra interna == false.
3. Ordena por id.asc().
**Evidências:** main.py:1011-1018.

### Fluxo 7 — Download de anexo
1. GET /uploads/{filename} com header Authorization.
2. Valida path traversal, consulta mensagem pelo url_anexo, verifica acesso ao ticket.
3. Retorna FileResponse com Cache-Control: private, no-store.
**Evidências:** main.py:1064-1134, lib/api.ts:86-96.

### Fluxo 8 — WebSocket (tempo real)
1. POST /tickets/{id}/ws-token obtém token WS (60 s).
2. Abre WS para /ws/tickets/{id}.
3. Primeiro frame: { type: "authenticate", token }.
4. Backend valida Origin, decodifica token, confere ticket_id, usuário ativo, acesso ao ticket.
5. Registra conexão. Envia { type: "authenticated" }.
6. REST dispara broadcast new_message / ticket_updated.
**Evidências:** main.py:1140-1286, TicketChatDialog.tsx:40-89.

### Fluxo 9 — Gestão de equipe de suporte
1. GET /equipe/ lista atendentes com disponibilidade e capacidade.
2. PATCH /equipe/{id} atualiza disponível e/ou capacidade_maxima.
3. Não há distribuição automática nem atribuição de tickets a atendentes.
**Evidências:** main.py:408-481, models.py:120-132.

### Fluxo 10 — Gestão de usuários e franquias
1. POST /usuarios/ cria usuário (apenas administrador).
2. GET /usuarios/ lista usuários (apenas administrador).
3. POST /usuarios/{id}/franquias cria/reativa vínculo.
4. DELETE /usuarios/{id}/franquias/{fid} soft delete (ativo = false).
5. POST /franquias/ cria franquia (telefone único).
**Evidências:** main.py:339-641, main.py:657-717.

---

## 5. Funcionalidades Integradas

| Funcionalidade | Endpoint | Estado |
|----------------|----------|--------|
| Login | POST /auth/login | Integrada |
| Dados do usuário | GET /auth/me | Integrada |
| Listar franquias | GET /franquias/ | Integrada |
| Listar usuários | GET /usuarios/ | Integrada |
| Criar ticket | POST /tickets/ | Integrada |
| Listar tickets | GET /tickets/ | Integrada |
| Alterar ticket | PATCH /tickets/{id} | Integrada |
| Enviar mensagem | POST /tickets/{id}/mensagens/ | Integrada |
| Listar mensagens | GET /tickets/{id}/mensagens/ | Integrada |
| Baixar anexo | GET /uploads/{filename} | Integrada |
| Token WebSocket | POST /tickets/{id}/ws-token | Integrada |
| WebSocket tempo real | WS /ws/tickets/{id} | Integrada |
| Listar equipe | GET /equipe/ | Integrada |
| Atualizar atendente | PATCH /equipe/{id} | Integrada |

Funcionalidades implementadas apenas no backend (sem tela frontend):
- Criar franquia (POST /franquias/)
- Criar usuário (POST /usuarios/)
- Vincular usuário a franquia (POST /usuarios/{id}/franquias)
- Desativar vínculo (DELETE /usuarios/{id}/franquias/{fid})

---

## 6. Funcionalidades Incompletas ou Ausentes

| Item | Status | Motivo |
|------|--------|--------|
| Ativação/desativação de franquia | Não identificada | Campo ativa existe no modelo, mas não há endpoint. |
| Desativação de usuário | Não identificada | Usuário só pode ser criado, não desativado via API. |
| GET /tickets/{id} (consulta individual) | Não identificada | Endpoint ausente. |
| Edição de mensagem | Não identificada | Endpoint ausente. |
| Exclusão de mensagem | Não identificada | Endpoint ausente. |
| Distribuição automática de tickets | Não identificada | Lógica ausente; capacidade_maxima e disponivel não têm efeito operacional. |
| Atribuição de ticket a atendente | Não identificada | Lógica ausente. |
| Objeto R / getAPIURL / R.services | Não encontrado | Não existe nesta versão. |
| Axios | Não encontrado | Frontend usa fetch nativo (lib/api.ts). |
| Socket.IO | Não encontrado | Backend e frontend usam WebSocket nativo. |
| Serviços chatAgents, chatIntegrator, ai, creditManagement, whatsapp | Não encontrados | Não existem no frontend nem backend. |

### Comportamentos parcialmente implementados

| Item | Descrição | Impacto |
|------|-----------|---------|
| Filtro de status na listagem | Frontend recebe parâmetro status mas ignora (void status). Backend não expõe o parâmetro. | Usuário não pode filtrar tickets por status via API. |
| Controle de status no chat | Frontend expõe select de status apenas para administrador e suporte_n1. Backend permite suporte_n2 também. | Suporte_n2 não pode alterar status via interface do chat. |
| Capacidade de atendente | capacidade_maxima e disponivel são armazenados mas não usados para limitar ou distribuir tickets. | Configuração sem efeito operacional. |
| Expiração de token WS | Token expira em 60 s sem renovação automática. | Conexão WebSocket pode cair silenciosamente após 1 minuto. |
| Perda de acesso ao ticket durante WS | Validação de acesso ocorre apenas no handshake. | Usuário pode continuar recebendo eventos após perder acesso. |

---

## 7. Riscos Técnicos e Funcionais

1. **Sem distribuição automática:** Tickets não são atribuídos automaticamente a atendentes. A configuração de capacidade e disponibilidade não tem efeito operacional.
2. **Sem edição/exclusão de mensagens:** Mensagens são imutáveis após criação. Não há como corrigir erros.
3. **Sem validação de transição de status:** Qualquer status pode ser definido para qualquer ticket (ex: de Encerrado para Aberto).
4. **Sem identificação de criador de ticket:** Não há registro de quem abriu cada ticket.
5. **Token WS de curta duração (60 s):** Pode causar desconexões frequentes se o frontend não renovar proativamente.
6. **Sem desconexão WS por perda de acesso:** Segurança potencialmente fraca se o acesso ao ticket for revogado durante uma sessão WS ativa.

---

## 8. Dúvidas que Dependem do Responsável pelo Produto

- Os serviços ausentes (chatAgents, chatIntegrator, ai, creditManagement, whatsapp) estão planejados para outra fase ou outro repositório?
- O objeto R / getAPIURL / R.services existe em alguma versão anterior ou branch diferente?
- O timeout de 15 s mencionado está implementado em alguma camada de infraestrutura (Nginx, balanceador)?
- A capacidade de atendente deve afetar a distribuição de tickets ou é apenas exibição?
- É necessário adicionar endpoints de edição/exclusão de mensagem e consulta individual de ticket?

---

## 9. Lista dos Arquivos Documentais Criados/Atualizados

| # | Arquivo | Conteúdo |
|---|---------|----------|
| 1 | docs\engenharia-reversa\10-regras-de-negocio.md | Regras de negócio por área (auth, franquias, tickets, mensagens, equipe, WebSocket) |
| 2 | docs\engenharia-reversa\11-matriz-de-permissoes.md | Matriz de permissões por endpoint + perfil/papel + diferenças frontend×backend |
| 3 | docs\engenharia-reversa\12-fluxos-operacionais.md | 10 fluxos reconstruídos com evidências de linha |
| 4 | docs\engenharia-reversa\13-jornadas-de-usuarios.md | 6 perfis (admin, suporte_n1, suporte_n2, proprietário, gerente, funcionário) |
| 5 | docs\engenharia-reversa\14-websocket-eventos.md | Eventos, handshake, erros, reconexão, filtro de internas |
| 6 | docs\engenharia-reversa\15-integracao-frontend-backend.md | Matriz funcionalidade×endpoint×estado de integração |
| 7 | docs\engenharia-reversa\16-lacunas-e-comportamentos-nao-implementados.md | Ausências, parciais, não identificados, riscos, dúvidas |
| 8 | docs\engenharia-reversa\00-relatorio-final-fase4.md | Este relatório consolidado (agregação dos 7 acima) |

---

**Próxima etapa recomendada:** Fase 4 concluída. Não implementar nada. Aguardar decisão do produto sobre as dúvidas da seção 8 antes de avançar para Fase 5 (reconstrução das regras de negócio e fluxos operacionais de chamados, mensagens, franquias e equipe).


