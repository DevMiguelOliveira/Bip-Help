# 12 — Fluxos Operacionais do BIPManager

Documento investigativo da Fase 4. Todos os fluxos abaixo foram extraídos da implementação real.

## Fluxo 1 — Autenticação

1. Usuário acessa tela de login (LoginPage.tsx).
2. Frontend envia POST /auth/login com username (e-mail) e password (application/x-www-form-urlencoded).
3. Backend normaliza o e-mail (strip().lower()), consulta usuario por e-mail.
4. Se usuário não existir, executa verify_password com hash dummy (mitigação de timing attack).
5. Se existir, verifica senha com pwdlib e checa ativo == true.
6. Em caso de sucesso, emite JWT (access token, 30 min, token_use=access) e retorna expires_in (30*60 segundos).
7. Frontend armazena token em localStorage (chave bip-access-token).
8. Frontend chama GET /auth/me para recuperar dados do usuário e franquias vinculadas.
9. Se qualquer requisição retornar 401, unauthorizedHandler dispara logout (remove localStorage).

Evidências: backend/auth.py:65-123, backend/main.py:259-324, temp_restore/frontend/src/services/auth.ts, temp_restore/frontend/src/context/AuthContext.tsx, temp_restore/frontend/src/lib/api.ts.

## Fluxo 2 — Criação de ticket

1. Usuário autenticado preenche franquia_id e descricao (1-10000 chars) na tela NewTicketDialog.
2. Frontend envia POST /tickets/ com corpo JSON { franquia_id, descricao }.
3. Backend verifica franquia ativa (verificar_franquia_ativa) e papel do usuário na franquia (get_franchise_role).
4. Cria registro em tickets com status padrão "Aberto".
5. Retorna TicketResponse { id, franquia_id, descricao, status, criado_em }.

Evidências: backend/main.py:734-753, backend/models.py:58-66, temp_restore/frontend/src/services/data.ts:23-26.

## Fluxo 3 — Listagem de tickets

1. Frontend envia GET /tickets/?limit=500 (opcionalmente ?franquia_id=N).
2. Backend filtra tickets por franquia_autorizada se usuário não for administrador/suporte.
3. Se franquia_id informado, valida papel do usuário naquela franquia.
4. Ordena por criado_em.desc(), id.desc(). Aplica paginação skip/limit.
5. Retorna lista de TicketResponse.

Nota: parâmetro status é recebido pelo frontend (getTickets) mas ignorado com void status; filtro de status é feito client-side.

Evidências: backend/main.py:764-807, temp_restore/frontend/src/services/data.ts:13-20.

## Fluxo 4 — Alteração de ticket (PATCH)

1. Frontend envia PATCH /tickets/{ticket_id} com { status } e/ou { descricao }.
2. Backend busca ticket (obter_ticket, 404 se não existir).
3. Valida verificar_acesso_ticket (papel na franquia).
4. Se não for suporte (administrador/suporte_n1/suporte_n2):
   - papel deve ser proprietario ou gerente (funcionario recebe 403).
   - não pode alterar status (403).
   - só pode editar se status == "Aberto" (409 se encerrado).
5. Se for suporte: pode alterar status e descricao.
6. Persiste alterações e faz broadcast do evento ticket_updated via WebSocket.
7. Retorna TicketResponse atualizado.

Evidências: backend/main.py:824-866.

## Fluxo 5 — Envio de mensagem

1. Frontend envia POST /tickets/{ticket_id}/mensagens/ com FormData (texto e/ou file).
2. Backend valida acesso ao ticket.
3. Se interna == true, verifica que o usuário é suporte (caso contrário 403).
4. Se houver arquivo: lê conteúdo (máx 20 MB), detecta tipo por assinatura binária (JPG/PNG/WEBP), salva em backend/uploads/ com nome uuid4.ext.
5. Cria registro em mensagens com remetente (nome), remetente_id (ID do usuário), texto, url_anexo, interna.
6. Faz broadcast do evento new_message para conexões WebSocket do ticket (pula internas para não-suporte).
7. Retorna MensagemResponse.

Evidências: backend/main.py:898-988, backend/models.py:97-109.

## Fluxo 6 — Listagem de mensagens

1. Frontend envia GET /tickets/{ticket_id}/mensagens/.
2. Backend valida acesso ao ticket.
3. Se usuário não for suporte, filtra mensagens interna == false.
4. Ordena por id.asc() e retorna lista.

Evidências: backend/main.py:1011-1018.

## Fluxo 7 — Download de anexo

1. Frontend chama privateFileUrl(/uploads/{filename}, token) que faz GET /uploads/{filename} com header Authorization.
2. Backend valida path traversal (filename sem /, \, ., ..).
3. Consulta mensagem pelo url_anexo e verifica acesso ao ticket.
4. Valida extensão (JPG/PNG/WEBP) e existência do arquivo físico.
5. Retorna FileResponse com Cache-Control: private, no-store.

Evidências: backend/main.py:1064-1134, temp_restore/frontend/src/lib/api.ts:86-96.

## Fluxo 8 — WebSocket (tempo real)

1. Frontend chama POST /tickets/{ticket_id}/ws-token para obter token WS (60 s de expiração).
2. Frontend abre WebSocket para wsBase + /ws/tickets/{ticket_id}.
3. Frontend envia primeiro frame JSON { type: "authenticate", token }.
4. Backend valida Origin header, decodifica token WS, confere ticket_id, valida usuário ativo e acesso ao ticket.
5. Registra conexão em ConnectionManager.active_connections[ticket_id] com is_support.
6. Envia { type: "authenticated", ticket_id }.
7. Quando nova mensagem é criada pela REST, backend faz broadcast do evento new_message (ou ticket_updated para PATCH de ticket).
8. Broadcast filtra mensagens internas para conexões não-suporte.
9. Frontend reconecta com exponential backoff (1s → 30s) em caso de desconexão.

Evidências: backend/main.py:1140-1286, temp_restore/frontend/src/pages/TicketChatDialog.tsx:40-89.

## Fluxo 9 — Gestão de equipe de suporte

1. GET /equipe/ lista atendentes (usuários com perfil_sistema suporte_n1 ou suporte_n2) com configuração de disponibilidade e capacidade. Requer administrador/suporte_n1/suporte_n2.
2. PATCH /equipe/{usuario_id} atualiza disponivel e/ou capacidade_maxima.
   - Administrador pode alterar qualquer atendente.
   - Atendente pode alterar apenas disponivel de si mesmo.
   - Só administrador pode alterar capacidade_maxima.
   - Atendente inativo não pode ficar disponível (409).
3. Não há distribuição automática de tickets nem atribuição de tickets a atendentes.

Evidências: backend/main.py:408-481, backend/models.py:120-132.

## Fluxo 10 — Gestão de usuários e franquias

1. POST /usuarios/ cria usuário (apenas administrador). Se perfil_sistema for suporte_n1/n2, cria AtendenteConfig.
2. GET /usuarios/ lista usuários (apenas administrador).
3. POST /usuarios/{id}/franquias cria ou reativa vínculo usuário-franquia (apenas administrador).
4. DELETE /usuarios/{id}/franquias/{fid} define ativo = false (soft delete).
5. POST /franquias/ cria franquia (apenas administrador). Telefone único.
6. GET /franquias/ lista franquias (não-admin vê apenas vinculadas e ativas).

Evidências: backend/main.py:339-641, backend/main.py:657-717.
