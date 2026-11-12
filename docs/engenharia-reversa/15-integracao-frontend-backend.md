# 15 — Integração Frontend × Backend

Documento investigativo da Fase 4. Matriz de funcionalidades com estado de implementação.

## Matriz de funcionalidades

| Funcionalidade | Tela/Componente | Serviço Frontend | Endpoint Backend | Schema Entrada | Schema Saída | Autorização | Persistência | Estado |
|----------------|-----------------|------------------|------------------|----------------|--------------|-------------|--------------|--------|
| Login | LoginPage.tsx | auth.ts login | POST /auth/login | OAuth2 form (username, password) | TokenResponse | Pública | leitura usuarios | Implementada e integrada |
| Dados do usuário | AuthContext | auth.ts getMe | GET /auth/me | — | UsuarioMeResponse | Bearer + ativo | leitura usuarios/franquias | Implementada e integrada |
| Listar franquias | FranchisesPage | data.ts getFranchises | GET /franquias/ | — | FranquiaResponse[] | Bearer | leitura franquias | Implementada e integrada |
| Criar franquia | (não há tela) | — | POST /franquias/ | FranquiaCreate | FranquiaResponse | administrador | grava franquias | Implementada apenas no backend |
| Criar usuário | (não há tela) | — | POST /usuarios/ | UsuarioCreate | UsuarioResponse | administrador | grava usuarios + atendente_config | Implementada apenas no backend |
| Listar usuários | UsersPage | data.ts getUsers | GET /usuarios/ | — | UsuarioResponse[] | administrador | leitura usuarios | Implementada e integrada |
| Vincular usuário-franquia | (não há tela) | — | POST /usuarios/{id}/franquias | UsuarioFranquiaCreate | UsuarioFranquiaResponse | administrador | grava usuario_franquias | Implementada apenas no backend |
| Desativar vínculo | (não há tela) | — | DELETE /usuarios/{id}/franquias/{fid} | — | UsuarioFranquiaResponse | administrador | atualiza usuario_franquias | Implementada apenas no backend |
| Criar ticket | NewTicketDialog | data.ts createTicket | POST /tickets/ | { franquia_id, descricao } | TicketResponse | Bearer + papel franquia | grava tickets | Implementada e integrada |
| Listar tickets | TicketsPage | data.ts getTickets | GET /tickets/ | — | TicketResponse[] | Bearer + vínculo franquia | leitura tickets | Implementada e integrada |
| Alterar ticket | TicketChatDialog (status) | data.ts updateTicket | PATCH /tickets/{id} | { status?, descricao? } | TicketResponse | Bearer + papel (status só suporte) | grava tickets | Parcialmente integrada (status apenas suporte_n1/n2 no frontend) |
| Enviar mensagem | TicketChatDialog | data.ts sendMessage | POST /tickets/{id}/mensagens/ | FormData (texto, file, interna) | MensagemResponse | Bearer + papel; interna só suporte | grava mensagens + uploads | Implementada e integrada |
| Listar mensagens | TicketChatDialog | data.ts getMessages | GET /tickets/{id}/mensagens/ | — | MensagemResponse[] | Bearer + papel; filtra internas | leitura mensagens | Implementada e integrada |
| Baixar anexo | MessageBubble | lib.ts privateFileUrl | GET /uploads/{filename} | — | arquivo binário | Bearer + acesso ticket | leitura arquivo físico | Implementada e integrada |
| Token WebSocket | TicketChatDialog | apiRequest POST | POST /tickets/{id}/ws-token | — | WebSocketTokenResponse | Bearer + acesso ticket | — | Implementada e integrada |
| WebSocket tempo real | TicketChatDialog | WebSocket nativo | WS /ws/tickets/{id} | { type, token } | eventos JSON | token WS + acesso ticket | memória (ConnectionManager) | Implementada e integrada |
| Listar equipe | TeamPage | data.ts getTeam | GET /equipe/ | — | AtendenteResponse[] | administrador/suporte_n1/suporte_n2 | leitura usuarios + atendente_config | Implementada e integrada |
| Atualizar atendente | TeamPage | data.ts updateAttendant | PATCH /equipe/{id} | AtendenteUpdate | AtendenteResponse | regras específicas | grava atendente_config | Implementada e integrada |
| Ativar/desativar franquia | — | — | (não existe endpoint) | — | — | — | — | Não identificada |
| Desativar usuário | — | — | (não existe endpoint) | — | — | — | — | Não identificada |
| Distribuição automática de tickets | — | — | (não existe) | — | — | — | — | Não identificada |
| Atribuição de ticket a atendente | — | — | (não existe) | — | — | — | — | Não identificada |
| Edição de mensagem | — | — | (não existe endpoint) | — | — | — | — | Não identificada |
| Exclusão de mensagem | — | — | (não existe endpoint) | — | — | — | — | Não identificada |
| Consulta individual de ticket | — | — | (não existe GET /tickets/{id}) | — | — | — | — | Não identificada |
| Filtro de status na listagem | TicketsPage | data.ts getTickets | (parâmetro ignorado, void status) | — | — | — | — | Parcial (frontend filtra client-side) |

## Serviços solicitados pelo usuário não encontrados

- chatAgents: não existe no frontend nem backend.
- chatIntegrator: não existe no frontend nem backend.
- ai: não existe no frontend nem backend.
- creditManagement: não existe no frontend nem backend.
- whatsapp: não existe no frontend nem backend.

## Diferenças frontend × backend

| Aspecto | Frontend | Backend | Impacto |
|---------|----------|---------|---------|
| Cliente HTTP | fetch nativo (api.ts) | FastAPI | Nenhuma incompatibilidade |
| Axios | Não utilizado | Não utilizado | — |
| Socket.IO | Não utilizado | Não utilizado | — |
| Objeto R / getAPIURL | Não encontrado | Não encontrado | Pista não se aplica a esta versão |
| Cache | TanStack Query staleTime 20s | — | Frontend controla cache |
| Retry | TanStack Query máx 1, pula 401/403 | — | Frontend controla retry |
| Timeout HTTP | Não definido explicitamente | Não definido no código | Pode estar em infraestrutura |
| Autenticação | localStorage (bip-access-token) | JWT HS256, Bearer | Coerente |
| Cookies | Não utilizados | Não utilizados | Coerente |
