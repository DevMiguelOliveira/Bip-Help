# 11 — Matriz de Permissões do BIPManager

Documento investigativo da Fase 4. Todas as permissões abaixo foram extraídas da implementação real. Nenhuma regra foi inventada.

## Perfis e papéis definidos no código

| Tipo | Valores | Localização |
|------|---------|-------------|
| perfil_sistema | administrador, suporte_n1, suporte_n2, NULL | backend/models.py:88-92 |
| papel (franquia) | proprietario, gerente, funcionario | backend/models.py:148-152 |

## Matriz de permissões por endpoint

| Endpoint | Método | Perfil permitido | Papel franquia permitido | Tabelas afetadas | Confiança | Evidência |
|----------|--------|------------------|--------------------------|------------------|-----------|-----------|
| / | GET | Público (nenhum) | Nenhum | — | confirmado | main.py:247 |
| /auth/login | POST | Público (nenhum) | Nenhum | usuarios (leitura) | confirmado | main.py:259 |
| /auth/me | GET | Qualquer autenticado ativo | Qualquer | usuarios, usuario_franquias, franquias | confirmado | main.py:291 |
| /usuarios/ | POST | administrador | Nenhum | usuarios, atendente_config | confirmado | main.py:339 |
| /usuarios/ | GET | administrador | Nenhum | usuarios | confirmado | main.py:382 |
| /usuarios/{id}/franquias | POST | administrador | Nenhum | usuarios, franquias, usuario_franquias | confirmado | main.py:526 |
| /usuarios/{id}/franquias/{fid} | DELETE | administrador | Nenhum | usuario_franquias | confirmado | main.py:617 |
| /franquias/ | GET | Qualquer autenticado | Vínculo ativo na franquia (se não-admin) | franquias, usuario_franquias | confirmado | main.py:657 |
| /franquias/ | POST | administrador | Nenhum | franquias | confirmado | main.py:696 |
| /tickets/ | POST | Qualquer autenticado | Papel na franquia (qualquer) | tickets | confirmado | main.py:734 |
| /tickets/ | GET | Qualquer autenticado | Vínculo ativo na franquia (se não-admin) | tickets | confirmado | main.py:764 |
| /tickets/{id} | PATCH | Qualquer autenticado | proprietario/gerente (descricao apenas); suporte (status+descricao) | tickets | confirmado | main.py:824 |
| /tickets/{id}/mensagens/ | POST | Qualquer autenticado | Papel na franquia (qualquer); interna apenas suporte | mensagens | confirmado | main.py:898 |
| /tickets/{id}/mensagens/ | GET | Qualquer autenticado | Papel na franquia (qualquer); não-suporte não vê internas | mensagens, tickets | confirmado | main.py:1011 |
| /uploads/{filename} | GET | Qualquer autenticado | Acesso ao ticket da mensagem | mensagens, tickets | confirmado | main.py:1064 |
| /tickets/{id}/ws-token | POST | Qualquer autenticado | Papel na franquia (qualquer) | usuarios, tickets | confirmado | main.py:1140 |
| WS /ws/tickets/{id} | WS | Token válido + acesso ao ticket | Papel na franquia (qualquer); is_support filtra internas | — (memória) | confirmado | main.py:1175 |

## Regras de autorização por perfil/papel

### administrador
- Acesso total a todos os endpoints administrativos.
- Pode criar usuários (POST /usuarios/), franquias (POST /franquias/), vincular usuários a franquias.
- Pode listar todos os usuários e franquias sem filtro.
- Pode alterar qualquer atendente (PATCH /equipe/{id}), incluindo capacidade_maxima.
- Pode alterar status e descrição de qualquer ticket.
- Pode criar notas internas em mensagens.

### suporte_n1 / suporte_n2
- Mesmo nível de acesso que administrador para tickets, mensagens, equipe e franquias (listagem).
- Não podem criar usuários (requer administrador).
- Não podem criar franquias (requer administrador).
- Não podem vincular usuários a franquias (requer administrador).
- Pode alterar disponibilidade própria (PATCH /equipe/{próprio id}, apenas disponivel).
- Não pode alterar capacidade_maxima de outro atendente (somente administrador).
- Pode criar notas internas em mensagens.
- Pode ver mensagens internas na listagem e WebSocket.

### proprietario / gerente (franquia)
- Pode criar tickets em franquias onde possui vínculo ativo.
- Pode listar tickets de suas franquias.
- Pode editar descrição de tickets abertos (PATCH /tickets/{id}, sem alterar status).
- Não pode alterar status de tickets (403).
- Não pode criar notas internas (403).
- Não pode ver mensagens internas (filtradas na listagem e WebSocket).
- Não pode gerenciar equipe de suporte (403 em /equipe/).

### funcionario (franquia)
- Pode criar tickets em franquias onde possui vínculo ativo.
- Pode listar tickets de suas franquias.
- Não pode editar tickets (papel funcionário não permite, 403 em PATCH /tickets/{id}).
- Não pode alterar status.
- Não pode criar notas internas.
- Não pode ver mensagens internas.
- Não pode gerenciar equipe de suporte.

### Usuário sem vínculo de franquia (perfil_sistema NULL, sem usuario_franquias ativo)
- Não pode criar tickets (get_franchise_role lança 403).
- Não pode listar tickets (sem franquias autorizadas).
- Não pode acessar /auth/me franquias (lista vazia).

## Diferenças entre frontend e backend

| Aspecto | Frontend | Backend | Status |
|---------|----------|---------|--------|
| Controle de status do ticket | Select exposto apenas para administrador e suporte_n1 (TicketChatDialog.tsx:118) | PATCH permite suporte_n2 também alterar status | Divergência parcial |
| Filtro de status na listagem | Parâmetro recebido mas ignorado (void status, data.ts:17-19) | Parâmetro status não existe no endpoint | Divergência |
| Autorização | Não impõe regras próprias; depende de 401/403 do backend | Aplica todas as regras via Depends | Comportamento divergente |

## Observações
- Não há distinção de comportamento entre suporte_n1 e suporte_n2 no código backend. Ambos têm as mesmas permissões.
- O papel funcionario de franquia não pode editar tickets nem criar notas internas.
- Não há endpoint de desativação de franquia nem de usuário (usuário só pode ser criado, não desativado via API).
