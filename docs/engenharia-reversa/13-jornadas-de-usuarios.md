# 13 — Jornadas de Usuários do BIPManager

Documento investigativo da Fase 4. Todas as jornadas abaixo são reconstruídas da implementação real do frontend e backend.

## 1. Administrador

### Telas acessíveis
- Login, Dashboard, Tickets, Users, Team, Franchises, Settings.

### Ações disponíveis
- Login e recuperação de dados (GET /auth/me).
- Criar usuário (POST /usuarios/).
- Listar usuários (GET /usuarios/).
- Criar franquia (POST /franquias/).
- Listar franquias (GET /franquias/).
- Criar ticket (POST /tickets/).
- Listar tickets (GET /tickets/).
- Alterar ticket (PATCH /tickets/{id}) — status e descrição.
- Enviar mensagem (POST /tickets/{id}/mensagens/), incluindo internas.
- Listar mensagens (GET /tickets/{id}/mensagens/).
- Baixar anexo (GET /uploads/{filename}).
- Obter token WebSocket (POST /tickets/{id}/ws-token) e conectar WS.
- Listar equipe (GET /equipe/).
- Atualizar atendente (PATCH /equipe/{id}) — qualquer atendente, incluindo capacidade.
- Vincular usuário a franquia (POST /usuarios/{id}/franquias).
- Desativar vínculo (DELETE /usuarios/{id}/franquias/{fid}).

### Requisições e endpoints
Conforme listado acima, todos com autenticação Bearer.

### Restrições
- Nenhuma restrição além de estar autenticado e ativo.

### Estados e feedbacks
- 401 se sessão expirada → logout.
- 409 se e-mail ou telefone duplicado.
- 201 em criações bem-sucedidas.

## 2. Suporte N1

### Telas acessíveis
- Login, Dashboard, Tickets, TicketChatDialog, Team.

### Ações disponíveis
- Mesmas do administrador, EXCETO: criar usuários, criar franquias, vincular usuários a franquias.
- Pode listar usuários e franquias.
- Pode alterar qualquer ticket (status e descrição).
- Pode criar notas internas.
- Pode alterar disponibilidade própria (PATCH /equipe/{próprio id}).
- Não pode alterar capacidade_maxima de outros (apenas administrador).

### Restrições
- 403 em POST /usuarios/, POST /franquias/, POST /usuarios/{id}/franquias (requerem administrador).

## 3. Suporte N2

### Telas acessíveis
- Idênticas ao Suporte N1.

### Ações disponíveis
- Idênticas ao Suporte N1 (sem distinção de comportamento no código backend).

### Restrições
- Idênticas ao Suporte N1.

### Observação
- Não há distinção de comportamento entre suporte_n1 e suporte_n2 na implementação backend.

## 4. Proprietário de franquia

### Telas acessíveis
- Login, Dashboard, Tickets, TicketChatDialog.

### Ações disponíveis
- Login e dados do usuário (GET /auth/me).
- Listar franquias vinculadas (GET /franquias/).
- Criar ticket em franquia vinculada (POST /tickets/).
- Listar tickets de suas franquias (GET /tickets/).
- Editar descrição de ticket aberto (PATCH /tickets/{id}, sem status).
- Enviar mensagem (POST /tickets/{id}/mensagens/), não-interna.
- Listar mensagens não-internas (GET /tickets/{id}/mensagens/).
- Baixar anexo (GET /uploads/{filename}).
- Conectar WebSocket no ticket.

### Restrições
- Não pode alterar status de ticket (403).
- Não pode criar notas internas (403).
- Não pode ver mensagens internas (filtradas).
- Não pode acessar /equipe/ (403).
- Não pode criar usuário ou franquia (403).

## 5. Gerente de franquia

### Telas acessíveis
- Idênticas ao Proprietário.

### Ações disponíveis
- Idênticas ao Proprietário.

### Restrições
- Idênticas ao Proprietário.

## 6. Funcionário de franquia

### Telas acessíveis
- Login, Dashboard, Tickets.

### Ações disponíveis
- Login e dados do usuário (GET /auth/me).
- Listar franquias vinculadas (GET /franquias/).
- Criar ticket em franquia vinculada (POST /tickets/).
- Listar tickets de suas franquias (GET /tickets/).
- Enviar mensagem (POST /tickets/{id}/mensagens/), não-interna.
- Listar mensagens não-internas (GET /tickets/{id}/mensagens/).
- Baixar anexo (GET /uploads/{filename}).
- Conectar WebSocket no ticket.

### Restrições
- Não pode editar ticket (403 em PATCH /tickets/{id}).
- Não pode alterar status.
- Não pode criar notas internas.
- Não pode ver mensagens internas.
- Não pode acessar /equipe/.
- Não pode criar usuário ou franquia.

## Comportamento de erro comum a todas as jornadas

- 401: credenciais inválidas ou sessão expirada → logout (remove localStorage).
- 403: sem permissão para a operação.
- 404: recurso não encontrado.
- 409: conflito (e-mail duplicado, telefone duplicado, ticket não aberto para edição, vínculo já ativo).
- 413: arquivo excede 20 MB.
- 415: formato de arquivo não permitido.
