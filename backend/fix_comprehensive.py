import re

# Read the current main.py
with open(r'D:\PROJETOS\BipHelp\backend\main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update ConnectionManager to track (WebSocket, is_support) tuples
old_connection_manager = '''class ConnectionManager:

    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    def connect(self, ticket_id: int, websocket: WebSocket):
        self.active_connections.setdefault(ticket_id, []).append(websocket)

    def disconnect(self, ticket_id: int, websocket: WebSocket):
        connections = self.active_connections.get(ticket_id, [])

        if websocket in connections:
            connections.remove(websocket)

        if not connections and ticket_id in self.active_connections:
            del self.active_connections[ticket_id]

    async def broadcast(self, ticket_id: int, message: dict):

        connections = list(
            self.active_connections.get(ticket_id, [])
        )

        for connection in connections:
            try:
                await connection.send_json(message)

            except (WebSocketDisconnect, RuntimeError):
                self.disconnect(ticket_id, connection)

            except Exception:
                logger.exception(\"Erro ao transmitir evento WebSocket.\")
                self.disconnect(ticket_id, connection)


manager = ConnectionManager()'''

new_connection_manager = '''class ConnectionManager:

    def __init__(self):
        self.active_connections: dict[int, list[tuple[WebSocket, bool]]] = {}

    def connect(self, ticket_id: int, websocket: WebSocket, is_support: bool = False):
        self.active_connections.setdefault(ticket_id, []).append((websocket, is_support))

    def disconnect(self, ticket_id: int, websocket: WebSocket):
        connections = self.active_connections.get(ticket_id, [])

        for i, (conn, _) in enumerate(connections):
            if conn is websocket:
                connections.pop(i)
                break

        if not connections and ticket_id in self.active_connections:
            del self.active_connections[ticket_id]

    async def broadcast(self, ticket_id: int, message: dict):

        connections = list(
            self.active_connections.get(ticket_id, [])
        )

        # Check if message is an internal note
        is_internal = message.get(\"interna\", False)

        for connection, is_support in connections:
            # Filter internal notes for non-support users
            if is_internal and not is_support:
                continue

            try:
                await connection.send_json(message)

            except (WebSocketDisconnect, RuntimeError):
                self.disconnect(ticket_id, connection)

            except Exception:
                logger.exception(\"Erro ao transmitir evento WebSocket.\")
                self.disconnect(ticket_id, connection)


manager = ConnectionManager()'''

content = content.replace(old_connection_manager, new_connection_manager)

# 2. Update emitir_token_websocket to include pode_criar_nota_interna
old_emitir_token = '''@app.post(
    \"/tickets/{ticket_id}/ws-token\",
    response_model=schemas.WebSocketTokenResponse
)
def emitir_token_websocket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):

    ticket = obter_ticket(db, ticket_id)

    verificar_acesso_ticket(
        db,
        current_user,
        ticket
    )

    token = create_websocket_token(
        user_id=current_user.id,
        ticket_id=ticket_id
    )

    return {
        \"token\": token,
        \"token_type\": \"websocket\",
        \"expires_in\": WEBSOCKET_TOKEN_EXPIRE_SECONDS
    }'''

new_emitir_token = '''@app.post(
    \"/tickets/{ticket_id}/ws-token\",
    response_model=schemas.WebSocketTokenResponse
)
def emitir_token_websocket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):

    ticket = obter_ticket(db, ticket_id)

    verificar_acesso_ticket(
        db,
        current_user,
        ticket
    )

    token = create_websocket_token(
        user_id=current_user.id,
        ticket_id=ticket_id
    )

    return {
        \"token\": token,
        \"token_type\": \"websocket\",
        \"expires_in\": WEBSOCKET_TOKEN_EXPIRE_SECONDS,
        \"pode_criar_nota_interna\": pode_criar_nota_interna(current_user)
    }'''

content = content.replace(old_emitir_token, new_emitir_token)

# 3. Update WebSocket endpoint to track is_support and pass to manager.connect
old_ws_endpoint = '''@app.websocket(\"/ws/tickets/{ticket_id}\")
async def websocket_endpoint(
    websocket: WebSocket,
    ticket_id: int
):

    connected = False

    # Somente o frontend publicado pode iniciar a conexÃ£o.
    origin = websocket.headers.get(\"origin\")

    if origin not in FRONTEND_ORIGINS:
        await websocket.close(code=1008)
        return

    await websocket.accept()

    try:

        # O token vai no primeiro frame, nÃ£o na URL.
        # Isso evita exposiÃ§Ã£o em logs de proxy e navegador.
        handshake = await asyncio.wait_for(
            websocket.receive_json(),
            timeout=5
        )

        if (
            not isinstance(handshake, dict)
            or handshake.get(\"type\") != \"authenticate\"
            or not isinstance(handshake.get(\"token\"), str)
        ):
            await websocket.close(code=1008)
            return

        payload = decode_websocket_token(
            handshake[\"token\"]
        )

        token_ticket_id = int(payload[\"ticket_id\"])
        user_id = int(payload[\"sub\"])

        if token_ticket_id != ticket_id:
            await websocket.close(code=1008)
            return

        # Valida identidade, estado e autorizaÃ§Ã£o no PostgreSQL.
        db = SessionLocal()

        try:

            user = db.get(models.Usuario, user_id)
            ticket = db.get(models.Ticket, ticket_id)

            if not user or not user.ativo or not ticket:
                await websocket.close(code=1008)
                return

            verificar_acesso_ticket(
                db,
                user,
                ticket
            )

        finally:
            db.close()

        manager.connect(
            ticket_id,
            websocket
        )

        connected = True

        await websocket.send_json(
            {
                \"type\": \"authenticated\",
                \"ticket_id\": ticket_id
            }
        )

        # O WebSocket Ã© destinado Ã  recepÃ§Ã£o de eventos.
        # Novas mensagens devem ser gravadas pela API REST.
        while True:

            data = await websocket.receive_text()

            if data == \"ping\":
                await websocket.send_json(
                    {\"type\": \"pong\"}
                )

            else:
                await websocket.send_json(
                    {
                        \"type\": \"error\",
                        \"detail\": \"Envie mensagens pela API REST.\"
                    }
                )

    except asyncio.TimeoutError:
        await websocket.close(code=1008)

    except WebSocketDisconnect:
        pass

    except (
        InvalidTokenError,
        ValueError,
        TypeError,
        HTTPException
    ):
        await websocket.close(code=1008)

    except Exception:
        logger.exception(\"Erro na conexÃ£o WebSocket.\")
        await websocket.close(code=1011)

    finally:

        if connected:
            manager.disconnect(ticket_id, websocket)'''

new_ws_endpoint = '''@app.websocket(\"/ws/tickets/{ticket_id}\")
async def websocket_endpoint(
    websocket: WebSocket,
    ticket_id: int
):

    connected = False

    # Somente o frontend publicado pode iniciar a conexÃ£o.
    origin = websocket.headers.get(\"origin\")

    if origin not in FRONTEND_ORIGINS:
        await websocket.close(code=1008)
        return

    await websocket.accept()

    try:

        # O token vai no primeiro frame, nÃ£o na URL.
        # Isso evita exposiÃ§Ã£o em logs de proxy e navegador.
        handshake = await asyncio.wait_for(
            websocket.receive_json(),
            timeout=5
        )

        if (
            not isinstance(handshake, dict)
            or handshake.get(\"type\") != \"authenticate\"
            or not isinstance(handshake.get(\"token\"), str)
        ):
            await websocket.close(code=1008)
            return

        payload = decode_websocket_token(
            handshake[\"token\"]
        )

        token_ticket_id = int(payload[\"ticket_id\"])
        user_id = int(payload[\"sub\"])

        if token_ticket_id != ticket_id:
            await websocket.close(code=1008)
            return

        # Valida identidade, estado e autorizaÃ§Ã£o no PostgreSQL.
        db = SessionLocal()

        try:

            user = db.get(models.Usuario, user_id)
            ticket = db.get(models.Ticket, ticket_id)

            if not user or not user.ativo or not ticket:
                await websocket.close(code=1008)
                return

            verificar_acesso_ticket(
                db,
                user,
                ticket
            )

            # Determine if user is support staff for internal note filtering
            is_support = user.perfil_sistema in (\"administrador\", \"suporte_n1\", \"suporte_n2\")

        finally:
            db.close()

        manager.connect(
            ticket_id,
            websocket,
            is_support=is_support
        )

        connected = True

        await websocket.send_json(
            {
                \"type\": \"authenticated\",
                \"ticket_id\": ticket_id
            }
        )

        # O WebSocket Ã© destinado Ã  recepÃ§Ã£o de eventos.
        # Novas mensagens devem ser gravadas pela API REST.
        while True:

            data = await websocket.receive_text()

            if data == \"ping\":
                await websocket.send_json(
                    {\"type\": \"pong\"}
                )

            else:
                await websocket.send_json(
                    {
                        \"type\": \"error\",
                        \"detail\": \"Envie mensagens pela API REST.\"
                    }
                )

    except asyncio.TimeoutError:
        await websocket.close(code=1008)

    except WebSocketDisconnect:
        pass

    except (
        InvalidTokenError,
        ValueError,
        TypeError,
        HTTPException
    ):
        await websocket.close(code=1008)

    except Exception:
        logger.exception(\"Erro na conexÃ£o WebSocket.\")
        await websocket.close(code=1011)

    finally:

        if connected:
            manager.disconnect(ticket_id, websocket)'''

content = content.replace(old_ws_endpoint, new_ws_endpoint)

# 4. Update the broadcast call in enviar_mensagem to include \"interna\" field
old_broadcast = '''    background_tasks.add_task(
        manager.broadcast,
        ticket_id,
        {
            \"type\": \"new_message\",
            \"id\": db_mensagem.id,
            \"ticket_id\": db_mensagem.ticket_id,
            \"remetente\": db_mensagem.remetente,
            \"remetente_id\": db_mensagem.remetente_id,
            \"texto\": db_mensagem.texto,
            \"url_anexo\": db_mensagem.url_anexo,
            \"criada_em\": db_mensagem.criada_em.isoformat(),
        }
    )'''

new_broadcast = '''    background_tasks.add_task(
        manager.broadcast,
        ticket_id,
        {
            \"type\": \"new_message\",
            \"id\": db_mensagem.id,
            \"ticket_id\": db_mensagem.ticket_id,
            \"remetente\": db_mensagem.remetente,
            \"remetente_id\": db_mensagem.remetente_id,
            \"texto\": db_mensagem.texto,
            \"url_anexo\": db_mensagem.url_anexo,
            \"interna\": db_mensagem.interna,
            \"criada_em\": db_mensagem.criada_em.isoformat(),
        }
    )'''

content = content.replace(old_broadcast, new_broadcast)

# 5. Change API title from \"BIPManager API\" to \"BipHelp API\"
content = content.replace(
    'title=\"BIPManager API\"',
    'title=\"BipHelp API\"'
)

# Write the fixed content
with open(r'D:\PROJETOS\BipHelp\backend\main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('All fixes applied successfully!')
