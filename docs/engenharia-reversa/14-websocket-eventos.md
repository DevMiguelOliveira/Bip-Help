# 14 — Eventos WebSocket do BIPManager

Documento investigativo da Fase 4. Todos os eventos abaixo foram extraídos da implementação real.

## Endpoint

- WS /ws/tickets/{ticket_id} (backend/main.py:1175).

## Handshake de autenticação

1. Frontend obtém token via POST /tickets/{ticket_id}/ws-token (backend/main.py:1140).
2. Token expira em 60 segundos (WEBSOCKET_TOKEN_EXPIRE_SECONDS = 60, backend/auth.py:186).
3. Frontend abre conexão WebSocket.
4. Primeiro frame deve ser JSON: { type: "authenticate", token: "<ws-token>" }.
5. Backend valida Origin header contra FRONTEND_ORIGINS.
6. Backend decodifica token WS, confere ticket_id, valida usuário ativo e acesso ao ticket.
7. Em caso de sucesso: registra conexão e envia { type: "authenticated", ticket_id }.
8. Em caso de falha: close(code=1008).

Evidências: backend/main.py:1183-1249, temp_restore/frontend/src/pages/TicketChatDialog.tsx:40-52.

## Eventos recebidos (servidor → cliente)

| Evento | Estrutura JSON | Quando é enviado |
|--------|----------------|------------------|
| authenticated | { "type": "authenticated", "ticket_id": <int> } | Após handshake bem-sucedido |
| ticket_updated | { "type": "ticket_updated", "ticket_id": <int>, "status": "<status>" } | Após PATCH /tickets/{id} (background task) |
| new_message | { "type": "new_message", "id": <int>, "ticket_id": <int>, "remetente": "<str>", "remetente_id": <int|null>, "texto": "<str|null>", "url_anexo": "<str|null>", "criada_em": "<iso>", "interna": <bool> } | Após POST /tickets/{id}/mensagens/ |
| error | { "type": "error", "detail": "<str>" } | Se cliente enviar texto que não seja "ping" |
| pong | { "type": "pong" } | Se cliente enviar texto "ping" |

Evidências: backend/main.py:976-988, backend/main.py:863-866, backend/main.py:1248-1273.

## Eventos enviados (cliente → servidor)

| Evento | Estrutura | Quando é enviado |
|--------|-----------|------------------|
| authenticate | { "type": "authenticate", "token": "<ws-token>" } | Primeiro frame após abertura da conexão |
| ping | "ping" (texto simples) | Opcional; backend responde pong |

Evidências: temp_restore/frontend/src/pages/TicketChatDialog.tsx:48, backend/main.py:1266-1269.

## Tratamento de erros

| Condição | Resposta | Localização |
|----------|----------|-------------|
| Origin inválida | close(1008) | backend/main.py:1183-1186 |
| Handshake inválido | close(1008) | backend/main.py:1208-1213 |
| Token WS inválido | close(1008) | backend/main.py:1219-1222 |
| ticket_id mismatch | close(1008) | backend/main.py:1225-1228 |
| Usuário inativo/inexistente | close(1008) | backend/main.py:1231-1234 |
| Sem acesso ao ticket | close(1008) | backend/main.py:1236-1239 |
| Timeout de handshake (5s) | close(1008) | backend/main.py:1203-1206 |
| Exceção genérica | close(1011) | backend/main.py:1279-1281 |

## Ping/pong

- O backend responde pong se receber texto "ping".
- O frontend não envia ping ativamente.
- Qualquer outro texto recebido pelo servidor gera evento error e mantém a conexão aberta.

Evidências: backend/main.py:1266-1273.

## Reconexão

- Frontend implementa exponential backoff em onclose e onerror.
- Delay: Math.min(1000 * 2 ** Math.min(retryCount, 5), 30000) (1s a 30s).
- retryCount incrementado a cada falha.
- Cleanup do useEffect fecha o socket e limpa timers.

Evidências: temp_restore/frontend/src/pages/TicketChatDialog.tsx:74-89.

## Expiração de token WS

- Token expira em 60 segundos.
- Não há renovação automática no frontend.
- A conexão deve ser reaberta com um novo token obtido via POST /tickets/{id}/ws-token.

## Encerramento de conexão

- manager.disconnect remove a conexão de active_connections[ticket_id].
- Se não houver mais conexões para o ticket, a entrada é deletada do dicionário.
- Frontend fecha o socket no cleanup do useEffect.

Evidências: backend/main.py:123-129, backend/main.py:1246-1248, temp_restore/frontend/src/pages/TicketChatDialog.tsx:89.

## Múltiplas conexões

- active_connections é dict[int, list[tuple[WebSocket, bool]]].
- Múltiplos clientes podem estar conectados ao mesmo ticket simultaneamente.
- is_support indica se a conexão pertence a equipe de suporte (filtro de mensagens internas).

Evidências: backend/main.py:108-112.

## Filtro de mensagens internas

- manager.broadcast verifica message.interna.
- Se interna == true e conexão não é suporte (is_support == false), a mensagem não é enviada.

Evidências: backend/main.py:139-141.

## Persistência vs tempo real

- Mensagens são persistidas pela REST (POST /tickets/{id}/mensagens/) ANTES do broadcast.
- WebSocket não persiste dados; apenas transmite eventos.
- Comentário no código: "O WebSocket é destinado à recepção de eventos. Novas mensagens devem ser gravadas pela API REST."

Evidências: backend/main.py:1258-1260.
