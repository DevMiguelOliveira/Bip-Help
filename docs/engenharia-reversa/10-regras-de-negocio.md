# 10 — Regras de Negócio do BIPManager

Documento investigativo da Fase 4. Todas as regras abaixo foram extraídas da implementação real do frontend e backend. Nenhuma funcionalidade foi inventada.

## 1. Identidade, autenticação e autorização

### 1.1 Processo de login
- **Confirmado no código.** Endpoint POST /auth/login (backend/main.py:259). Recebe OAuth2PasswordRequestForm (username = e-mail, password).
- A função authenticate_user em backend/auth.py:65 normaliza o e-mail (strip().lower()), consulta usuarios por e-mail, e se não encontrar, executa verify_password com um hash dummy para mitigar timing attack (backend/auth.py:74-78).
- Senha validada com verify_password (backend/auth.py:79-80). Usuário inativo (ativo = false) retorna None (backend/auth.py:82).
- Em caso de falha, retorna HTTP 401 com WWW-Authenticate: Bearer (backend/main.py:278-282).
- Token emitido com create_access_token(user.id) (backend/auth.py:100). Expiração padrão 30 minutos (ACCESS_TOKEN_EXPIRE_MINUTES = 30, backend/auth.py:43). Payload inclui sub, iss, aud, iat, exp, token_use: "access".
- Frontend armazena o token em localStorage chave bip-access-token (temp_restore/frontend/src/context/AuthContext.tsx:15). Não há uso de cookies.

### 1.2 Validação de credenciais
- **Confirmado no código.** get_current_user em backend/auth.py:91 decodifica o JWT com jwt.decode exigindo exp, iat, sub, iss, aud e verificando token_use == "access" (backend/auth.py:106-118). Usuário inexistente ou inativo gera HTTP 401 (backend/auth.py:121-123).
- O esquema OAuth2 usa tokenUrl="/auth/login" (backend/auth.py:89).

### 1.3 Emissão, validação e expiração de JWT
- **Confirmado no código.** Segredo lido de /etc/bipmanager/jwt_secret (backend/auth.py:20). Mínimo 64 caracteres (backend/auth.py:24-26). Algoritmo HS256 (backend/auth.py:27).
- Access token: 30 min. WebSocket token: 60 s (WEBSOCKET_TOKEN_EXPIRE_SECONDS = 60, backend/auth.py:186).
- WS token payload inclui ticket_id e token_use: "websocket" (backend/auth.py:188-200). Validação em decode_websocket_token exige ticket_id (backend/auth.py:211-221).

### 1.4 Recuperação dos dados do usuário autenticado
- **Confirmado no código.** GET /auth/me (backend/main.py:291) retorna UsuarioMeResponse com dados do usuário e lista de franquias ativas vinculadas (backend/main.py:304-324). Frontend chama getMe(token) (temp_restore/frontend/src/services/auth.ts:10).

### 1.5 Perfis e papéis
- **Confirmado no código.** perfil_sistema (coluna de usuarios): administrador, suporte_n1, suporte_n2, ou NULL (backend/models.py:88-92, check constraint ck_usuarios_perfil_sistema). Papel de franquia (papel em usuario_franquias): proprietario, gerente, funcionario (backend/models.py:148-152, check constraint ck_usuario_franquias_papel).
- Usuários administrativos (perfil_sistema não nulo) não recebem papel por franquia (backend/main.py:573-575).

### 1.6 Associação de usuários a franquias
- **Confirmado no código.** Tabela usuario_franquias com PK composta (usuario_id, franquia_id) (backend/models.py:140-143). Vínculo pode ser desativado (ativo = false) mas não excluído pelo endpoint DELETE.

### 1.7 Restrições de acesso por franquia
- **Confirmado no código.** get_franchise_role em backend/auth.py:133-161 verifica vínculo ativo na franquia para usuários não-administrativos. Administradores e suporte têm acesso irrestrito (backend/auth.py:136-139).
- user_can_access_ticket em backend/auth.py:163-172 delega para get_franchise_role com ticket.franquia_id.

### 1.8 Diferenças de autorização entre frontend e backend
- **Não identificado.** O frontend não impõe autorização própria; depende das respostas HTTP do backend (401/403). Não há regras de permissão duplicadas no frontend.

### 1.9 Comportamento de usuários inativos
- **Confirmado no código.** authenticate_user rejeita ativo = false (backend/auth.py:82). get_current_user rejeita ativo = false (backend/auth.py:122). Login de usuário inativo retorna 401.
- Vínculo de franquia inativo não filra automaticamente tickets? Na listagem de tickets não-admin, filtra franquias_autorizadas apenas com franquia.ativa.is_(True) (backend/main.py:781-785).

## 2. Franquias e usuários

### 2.1 Cadastro de franquias
- **Confirmado no código.** POST /franquias/ (backend/main.py:696). Apenas administrador (require_system_role("administrador")). Campos: nome_responsavel, unidade, telefone. Telefone é unique (backend/models.py:52). Conflito retorna 409 (Este telefone já pertence a outra franquia) (backend/main.py:714-717).

### 2.2 Consulta e listagem
- **Confirmado no código.** GET /franquias/ (backend/main.py:657). Usuários não-administrativos veem apenas franquias com vínculo ativo e franquia ativa (backend/main.py:669-678). Paginação skip/limit (backend/main.py:662-663).

### 2.3 Ativação e desativação
- **Não identificado.** Não há endpoint para alterar ativa de franquia. O campo existe no modelo (backend/models.py:54) e no schema (FranquiaResponse inclui ativa), mas não há rota PATCH/PUT para franquias.

### 2.4 Cadastro de usuários
- **Confirmado no código.** POST /usuarios/ (backend/main.py:339). Apenas administrador. Campos: nome (2-150), email (único), senha (14-128), perfil_sistema opcional (backend/schemas.py:132-152). Se perfil_sistema for suporte_n1 ou suporte_n2, cria AtendenteConfig (backend/main.py:364-366). E-mail duplicado retorna 409 (backend/main.py:371-374).

### 2.5 Associação e remoção de vínculos com franquias
- **Confirmado no código.** POST /usuarios/{usuario_id}/franquias (backend/main.py:526) cria ou reativa vínculo. DELETE /usuarios/{usuario_id}/franquias/{franquia_id} (backend/main.py:617) define ativo = False (soft delete).

### 2.6 Regras de unicidade
- **Confirmado no código.** E-mail de usuário único (unique=True, backend/models.py:71). Telefone de franquia único (unique=True, backend/models.py:52). PK composta de usuario_franquias impede vínculo duplicado (backend/models.py:140-143).

### 2.7 Restrições de exclusão
- **Confirmado no código.** ondelete="CASCADE" em usuario_franquias.usuario_id e .franquia_id (backend/models.py:141-142). ondelete="SET NULL" em mensagens.remetente_id (backend/models.py:102-105).

### 2.8 Efeitos de vínculos inativos
- **Confirmado no código.** Listagem de franquias não-admin filtra UsuarioFranquia.ativo.is_(True) (backend/main.py:674). Listagem de tickets não-admin filtra franquias ativas e vinculadas ativas (backend/main.py:781-785).

### 2.9 Informações retornadas ao usuário autenticado
- **Confirmado no código.** GET /auth/me retorna UsuarioResponse + franquias[] com franquia_id, unidade, nome_responsavel, papel, ativa (backend/main.py:304-324, schemas.py:192-197).

## 3. Tickets

### 3.1 Criação
- **Confirmado no código.** POST /tickets/ (backend/main.py:734). Qualquer usuário autenticado. Requer franquia_id e descricao (1-10000 chars). Verifica franquia ativa (verificar_franquia_ativa) e papel do usuário na franquia (get_franchise_role) (backend/main.py:744-748).

### 3.2 Associação à franquia
- **Confirmado no código.** ticket.franquia_id é FK obrigatória (backend/models.py:60). Não há campo de usuário responsável pela abertura (remetente não existe em tickets).

### 3.3 Identificação do usuário responsável pela abertura
- **Não identificado.** A tabela tickets não tem coluna de usuário criador. Não há registro de quem abriu o ticket.

### 3.4 Listagem e filtros
- **Confirmado no código.** GET /tickets/ (backend/main.py:764). Filtro opcional franquia_id (requer papel na franquia). Não-admin vê apenas tickets de suas franquias ativas vinculadas. Ordena por criado_em.desc(), id.desc() (backend/main.py:800-802). Paginação skip/limit. Parâmetro status é aceito na URL? Não — o schema da função não declara status query param. O frontend getTickets recebe status mas faz void status e filtra client-side (temp_restore/frontend/src/services/data.ts:17-19).

### 3.5 Consulta individual
- **Não identificado.** Não existe endpoint GET /tickets/{id}. Existe PATCH /tickets/{id} e GET /tickets/{id}/mensagens/, mas não consulta individual de ticket.

### 3.6 Alteração de descrição
- **Confirmado no código.** PATCH /tickets/{ticket_id} (backend/main.py:824). Permite alterar status e descricao. Não-suporte não pode alterar status (backend/main.py:852-855). Não-suporte só pode editar se status for Aberto (backend/main.py:856-859). Somente proprietário/gerente da franquia (não-funcionario) pode editar (backend/main.py:848-851).

### 3.7 Alteração de status
- **Confirmado no código.** Via PATCH /tickets/{ticket_id}. Apenas administrador, suporte_n1, suporte_n2 podem alterar status (backend/main.py:852-855). Frontend expõe select de status apenas para administrador e suporte_n1 (temp_restore/frontend/src/pages/TicketChatDialog.tsx:118).

### 3.8 Encerramento
- **Confirmado (via status).** Status Encerrado é um dos valores de TicketStatus (Literal["Aberto", "Em Atendimento", "Encerrado"], backend/schemas.py:40). Não há endpoint dedicado de encerramento; é feito via PATCH alterando status.

### 3.9 Restrições de acesso
- **Confirmado no código.** verificar_acesso_ticket chama get_franchise_role com ticket.franquia_id (backend/main.py:850). Não-admin sem papel na franquia recebe 403.

### 3.10 Diferenças entre franquia e suporte
- **Confirmado no código.** Franquia (proprietário/gerente): pode editar descrição de tickets abertos, não pode alterar status. Funcionário: não pode editar ticket (papel não permite, backend/main.py:848-851). Suporte: pode alterar status e descrição.

### 3.11 Transições de status
- **Confirmado no código.** Três estados: Aberto, Em Atendimento, Encerrado. Não há máquina de estados; qualquer transição entre eles é permitida via PATCH (sem validação de transição inválida). O frontend não bloqueia transições específicas.

## 4. Mensagens e anexos

### 4.1 Criação de mensagens
- **Confirmado no código.** POST /tickets/{ticket_id}/mensagens/ (backend/main.py:898). Requer texto ou file. Campo interna (bool, default false) só permitido para equipe de suporte (backend/main.py:918-922).

### 4.2 Identificação do remetente
- **Confirmado no código.** remetente = current_user.nome, remetente_id = current_user.id (backend/main.py:947-948).

### 4.3 Uso dos campos remetente e remetente_id
- **Confirmado no código.** remetente é string (nome), remetente_id é FK opcional para usuarios.id (SET NULL) (backend/models.py:100-105).

### 4.4 Associação da mensagem ao ticket
- **Confirmado no código.** ticket_id é FK obrigatório (backend/models.py:99).

### 4.5 Envio e recuperação de anexos
- **Confirmado no código.** Upload via multipart/form-data com campo file. Validação: máximo 20 MB (MAX_UPLOAD_BYTES = 20 * 1024 * 1024, backend/main.py:39), extensão JPG/PNG/WEBP detectada por assinatura binária (detectar_imagem, backend/main.py:52-70). Arquivo salvo em UPLOAD_DIR (backend/uploads/) com nome uuid4.ext. URL: /uploads/{nome_seguro} (backend/main.py:933-939).
- Recuperação: GET /uploads/{filename} (backend/main.py:1064). Requer autenticação e acesso ao ticket da mensagem. Valida path traversal (filename não pode conter /, \, ., ..) (backend/main.py:1073-1081).

### 4.6 Localização física dos arquivos
- **Confirmado no código.** UPLOAD_DIR = Path(__file__).resolve().parent / "uploads" → backend/uploads/ (backend/main.py:36-38).

### 4.7 Validação de extensão, tamanho e tipo
- **Confirmado no código.** Tamanho: 20 MB (413 se exceder, backend/main.py:924-928). Tipo: assinatura binária (415 se não for imagem, backend/main.py:929-932).

### 4.8 Autorização para acessar anexos
- **Confirmado no código.** GET /uploads/{filename} consulta a mensagem pelo url_anexo, verifica acesso ao ticket (verificar_acesso_ticket) (backend/main.py:1088-1103).

### 4.9 Notas internas
- **Confirmado no código.** Campo interna Boolean default false (backend/models.py:107-109). Apenas suporte (administrador, suporte_n1, suporte_n2) pode criar (backend/main.py:918-922). Não-suporte não vê mensagens internas na listagem (backend/main.py:1015-1018).

### 4.10 Regras de visibilidade das mensagens
- **Confirmado no código.** listar_mensagens filtra interna == False para não-suporte (backend/main.py:1015-1018). WebSocket ConnectionManager.broadcast pula internas para não-suporte (backend/main.py:139-141).

### 4.11 Diferenças entre mensagens comuns e internas
- **Confirmado no código.** Internas visíveis apenas para suporte. Não-suporte não pode criá-las nem listá-las.

### 4.12 Edição ou exclusão de mensagens
- **Não identificado.** Não existe endpoint PATCH /mensagens/{id} nem DELETE /mensagens/{id}. Mensagens são imutáveis após criação.

## 5. Equipe de suporte

### 5.1 Cadastro e configuração de atendentes
- **Confirmado no código.** Usuário com perfil_sistema suporte_n1 ou suporte_n2 criado via POST /usuarios/ gera automaticamente AtendenteConfig (backend/main.py:364-366). Configuração: disponivel (default true), capacidade_maxima (default 10, check ≥ 1) (backend/models.py:123-132).

### 5.2 Disponibilidade
- **Confirmado no código.** AtendenteConfig.disponivel Boolean. Atendente inativo não pode ficar disponível (409, backend/main.py:447-450).

### 5.3 Capacidade máxima
- **Confirmado no código.** AtendenteConfig.capacidade_maxima Integer ≥ 1. Apenas administrador pode alterar (backend/main.py:476-479). Atendente próprio pode alterar apenas disponivel (backend/main.py:464-475).

### 5.4 Atualização das configurações
- **Confirmado no código.** PATCH /equipe/{usuario_id} (backend/main.py:408). AtendenteUpdate com disponivel e/ou capacidade_maxima (backend/schemas.py:178-183).

### 5.5 Perfis autorizados
- **Confirmado no código.** GET /equipe/ requer administrador, suporte_n1 ou suporte_n2 (backend/main.py:414-418). PATCH /equipe/{id} requer autenticação; administrador edita qualquer um, atendente edita só si mesmo (disponivel) (backend/main.py:426-475).

### 5.6 Relação entre capacidade e tickets em atendimento
- **Não identificado.** Não há lógica que use capacidade_maxima ou disponivel para contar tickets em atendimento ou limitar atribuição.

### 5.7 Distribuição automática de tickets
- **Não identificado.** Não existe endpoint, serviço ou lógica de distribuição automática. capacidade_maxima e disponivel são apenas configurações armazenadas.

### 5.8 Atribuição de tickets a atendentes
- **Não identificado.** A tabela tickets não tem coluna de atendente responsável. Não há endpoint de atribuição.

## 6. Comunicação em tempo real (WebSocket)

### 6.1 Fluxo completo
1. Usuário abre ticket (via POST /tickets/).
2. Frontend solicita token WS: POST /tickets/{id}/ws-token (TicketChatDialog.tsx:20-23).
3. Backend valida autorização (verificar_acesso_ticket) e emite token de 60 s (backend/main.py:1140-1167).
4. Frontend estabelece WebSocket para wsBase + /ws/tickets/{id} (TicketChatDialog.tsx:42).
5. Frontend envia primeiro frame JSON {type: "authenticate", token} (TicketChatDialog.tsx:48).
6. Backend valida token WS, ticket_id, usuário ativo, acesso ao ticket (backend/main.py:1193-1236).
7. Conexão registrada em ConnectionManager.active_connections[ticket_id] (backend/main.py:1246).
8. Eventos transmitidos via manager.broadcast (backend/main.py:145-158).
9. Mensagens persistidas pela REST (POST /tickets/{id}/mensagens/), depois broadcast (backend/main.py:976-988).
10. WebSocket notifica clientes conectados.

### 6.2 Eventos recebidos (cliente ← servidor)
- **Confirmado no código.** authenticated ({type: "authenticated", ticket_id}), ticket_updated ({type: "ticket_updated", ticket_id, status}), new_message ({type: "new_message", id, ticket_id, remetente, remetente_id, texto, url_anexo, criada_em, interna}), error ({type: "error", detail}), pong ({type: "pong"}) (backend/main.py:1248-1253 + 976-988 + 863-866).

### 6.3 Eventos enviados (cliente → servidor)
- **Confirmado no código.** Handshake {type: "authenticate", token}; ping (texto) → resposta pong. Qualquer outro texto → error "Envie mensagens pela API REST." (backend/main.py:1266-1273).

### 6.4 Tratamento de erros
- **Confirmado no código.** Origem inválida → close 1008. Handshake inválido → close 1008. Token inválido → close 1008. ticket_id mismatch → close 1008. Usuário inativo ou inexistente → close 1008. Sem acesso ao ticket → close 1008 (backend/main.py:1183-1236). Exceção genérica → close 1011 (backend/main.py:1279).

### 6.5 Ping/pong
- **Confirmado no código.** Frontend não envia ping ativamente; backend responde pong se receber texto "ping" (backend/main.py:1266-1269).

### 6.6 Reconexão
- **Confirmado no código.** Frontend: exponential backoff (1s → 30s, Math.min(1000 * 2 ** min(retryCount, 5), 30000)) em onclose e onerror (TicketChatDialog.tsx:74-83). Timeout de handshake 5 s → close 1008 (backend/main.py:1203-1206).

### 6.7 Expiração de token
- **Confirmado no código.** WS token expira em 60 s (create_websocket_token). Não há renovação automática no frontend; a conexão deve ser reaberta com novo token.

### 6.8 Encerramento de conexão
- **Confirmado no código.** manager.disconnect remove a conexão (backend/main.py:123-129). Frontend socket?.close() no cleanup do useEffect (TicketChatDialog.tsx:89).

### 6.9 Múltiplas conexões
- **Confirmado no código.** ConnectionManager.active_connections é dict[int, list[tuple[WebSocket, bool]]], permite múltiplos WebSockets por ticket_id (backend/main.py:108-112).

### 6.10 Perda de acesso ao ticket
- **Não identificado.** Não há mecanismo que desconecte WS se o usuário perder acesso ao ticket durante a conexão. A validação ocorre apenas no handshake.

### 6.11 Filtros de mensagens internas
- **Confirmado no código.** broadcast salta interna == True para conexões is_support == False (backend/main.py:139-141).

## 7. Matriz resumida de regras

| Área | Regra | Confiança | Evidência |
|------|-------|-----------|-----------|
| Login | E-mail normalizado (lower, trim) | confirmado | auth.py:65 |
| Login | Hash dummy para timing attack | confirmado | auth.py:74-78 |
| JWT | Segredo em /etc/bipmanager/jwt_secret | confirmado | auth.py:20-26 |
| JWT | Access token 30 min | confirmado | auth.py:43, 100 |
| JWT | WS token 60 s | confirmado | auth.py:186 |
| Usuário inativo | Bloqueado no login e na validação de token | confirmado | auth.py:82, 122 |
| Franquia | Telefone único | confirmado | models.py:52 |
| Usuário | E-mail único | confirmado | models.py:71 |
| Vínculo franquia | PK composta, soft delete via ativo=false | confirmado | models.py:140-143, main.py:617-641 |
| Ticket | Nenhum campo de usuário criador | confirmado | models.py:58-66 |
| Ticket | Status: Aberto / Em Atendimento / Encerrado | confirmado | schemas.py:40 |
| Ticket | Sem validação de transição de status | confirmado | main.py:824-866 |
| Mensagem | interna só para suporte | confirmado | main.py:918-922 |
| Mensagem | Não-suporte não vê internas | confirmado | main.py:1015-1018 |
| Anexo | Máximo 20 MB, JPG/PNG/WEBP | confirmado | main.py:39, 924-932 |
| Anexo | Armazenado em backend/uploads/ | confirmado | main.py:36-38, 933-939 |
| WebSocket | Token no primeiro frame, não na URL | confirmado | main.py:1203-1206 |
| WebSocket | Filtro de internas por is_support | confirmado | main.py:139-141 |
| Equipe | Distribuição automática de tickets | não identificada | ausente no código |
| Equipe | Atribuição de tickets a atendente | não identificada | ausente no código |
| Cadastro franquia | Ativação/desativação via endpoint | não identificada | ausente no código |
