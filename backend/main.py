<<<<<<< HEAD
﻿
=======

>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
import asyncio
import logging
import os
import uuid

from pathlib import Path
from typing import Optional

from fastapi import (
    FastAPI,
<<<<<<< HEAD
    BackgroundTasks,
=======
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    WebSocket,
    WebSocketDisconnect,
    Query,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from jwt.exceptions import InvalidTokenError

import models
import schemas

from database import engine, SessionLocal

from auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    WEBSOCKET_TOKEN_EXPIRE_SECONDS,
    authenticate_user,
    create_access_token,
    create_websocket_token,
    decode_websocket_token,
    get_current_user,
    get_db,
    get_franchise_role,
    get_password_hash,
    require_system_role,
<<<<<<< HEAD
    pode_criar_nota_interna,
=======
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
)


# =========================================================
# CONFIGURACAO GERAL
# =========================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bipmanager")

app = FastAPI(
<<<<<<< HEAD
    title="BipHelp API",
    version="2.0.0",
    description="Plataforma de Helpdesk e gestÃ£o de suporte BIP360."
=======
    title="BIPManager API",
    version="2.0.0",
    description="Plataforma de Helpdesk e gestão de suporte BIP360."
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
)

FRONTEND_ORIGINS = [
    "https://bip-manager.lovable.app",
    "http://127.0.0.1:5173",
<<<<<<< HEAD
    "http://localhost:5173",
=======
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
    ],
    max_age=600,
)


# =========================================================
# ARMAZENAMENTO PRIVADO DE ANEXOS
# =========================================================

UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_BYTES = 20 * 1024 * 1024

IMAGE_FORMATS = {
    "jpg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
}


def detectar_imagem(conteudo: bytes):
    """
<<<<<<< HEAD
    Identifica o formato real do arquivo pela assinatura binÃ¡ria.
    NÃ£o confia no nome ou Content-Type enviado pelo navegador.
=======
    Identifica o formato real do arquivo pela assinatura binária.
    Não confia no nome ou Content-Type enviado pelo navegador.
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
    """

    if conteudo.startswith(b"\xff\xd8\xff"):
        return "jpg"

    if conteudo.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"

    if (
        len(conteudo) >= 12
        and conteudo[:4] == b"RIFF"
        and conteudo[8:12] == b"WEBP"
    ):
        return "webp"

    return None


# =========================================================
# GERENCIAMENTO DE WEBSOCKETS
# =========================================================

class ConnectionManager:

    def __init__(self):
<<<<<<< HEAD
        self.active_connections: dict[int, list[tuple[WebSocket, bool]]] = {}

    def connect(self, ticket_id: int, websocket: WebSocket, is_support: bool = False):
        self.active_connections.setdefault(ticket_id, []).append((websocket, is_support))
=======
        self.active_connections: dict[int, list[WebSocket]] = {}

    def connect(self, ticket_id: int, websocket: WebSocket):
        self.active_connections.setdefault(ticket_id, []).append(websocket)
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806

    def disconnect(self, ticket_id: int, websocket: WebSocket):
        connections = self.active_connections.get(ticket_id, [])

<<<<<<< HEAD
        for i, (conn, _) in enumerate(connections):
            if conn is websocket:
                connections.pop(i)
                break
=======
        if websocket in connections:
            connections.remove(websocket)
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806

        if not connections and ticket_id in self.active_connections:
            del self.active_connections[ticket_id]

    async def broadcast(self, ticket_id: int, message: dict):

        connections = list(
            self.active_connections.get(ticket_id, [])
        )

<<<<<<< HEAD
        # Check if message is an internal note
        is_internal = message.get("interna", False)

        for connection, is_support in connections:
            # Filter internal notes for non-support users
            if is_internal and not is_support:
                continue

=======
        for connection in connections:
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
            try:
                await connection.send_json(message)

            except (WebSocketDisconnect, RuntimeError):
                self.disconnect(ticket_id, connection)

            except Exception:
                logger.exception("Erro ao transmitir evento WebSocket.")
                self.disconnect(ticket_id, connection)


manager = ConnectionManager()


# =========================================================
# FUNCOES AUXILIARES
# =========================================================

def obter_ticket(
    db: Session,
    ticket_id: int
):
    ticket = (
        db.query(models.Ticket)
        .filter(models.Ticket.id == ticket_id)
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
<<<<<<< HEAD
            detail="Ticket nÃ£o encontrado."
=======
            detail="Ticket não encontrado."
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        )

    return ticket


def verificar_acesso_ticket(
    db: Session,
    current_user: models.Usuario,
    ticket: models.Ticket
):
    return get_franchise_role(
        db,
        current_user,
        ticket.franquia_id
    )


def verificar_franquia_ativa(
    db: Session,
    franquia_id: int
):
    franquia = (
        db.query(models.Franquia)
        .filter(models.Franquia.id == franquia_id)
        .first()
    )

    if not franquia:
        raise HTTPException(
            status_code=404,
<<<<<<< HEAD
            detail="Franquia nÃ£o encontrada."
=======
            detail="Franquia não encontrada."
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        )

    if not franquia.ativa:
        raise HTTPException(
            status_code=409,
<<<<<<< HEAD
            detail="Esta franquia estÃ¡ inativa."
=======
            detail="Esta franquia está inativa."
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        )

    return franquia


# =========================================================
# STATUS DA API
# =========================================================

@app.get("/")
def root():
    return {
        "status": "BIPManager Backend Operante",
        "versao": "2.0.0"
    }


# =========================================================
# AUTENTICACAO
# =========================================================

@app.post(
    "/auth/login",
    response_model=schemas.TokenResponse
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    # O campo OAuth2 username recebe o e-mail.
    user = authenticate_user(
        db,
        form_data.username,
        form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
<<<<<<< HEAD
            detail="E-mail ou senha invÃ¡lidos.",
=======
            detail="E-mail ou senha inválidos.",
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@app.get(
    "/auth/me",
    response_model=schemas.UsuarioMeResponse
)
def usuario_autenticado(
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    vinculos = (
        db.query(models.UsuarioFranquia, models.Franquia)
        .join(
            models.Franquia,
            models.UsuarioFranquia.franquia_id == models.Franquia.id
        )
        .filter(
            models.UsuarioFranquia.usuario_id == current_user.id,
            models.UsuarioFranquia.ativo.is_(True),
            models.Franquia.ativa.is_(True)
        )
        .order_by(models.Franquia.unidade)
        .all()
    )

    franquias = [
        {
            "franquia_id": vinculo.franquia_id,
            "unidade": franquia.unidade,
            "nome_responsavel": franquia.nome_responsavel,
            "papel": vinculo.papel,
            "ativa": franquia.ativa
        }
        for vinculo, franquia in vinculos
    ]

    resultado = schemas.UsuarioResponse.model_validate(
        current_user
    ).model_dump()

    resultado["franquias"] = franquias

    return resultado


# =========================================================
# GESTAO DE USUARIOS - SOMENTE ADMINISTRADOR
# =========================================================

@app.post(
    "/usuarios/",
    response_model=schemas.UsuarioResponse,
    status_code=201
)
def criar_usuario(
    usuario: schemas.UsuarioCreate,
    db: Session = Depends(get_db),
    administrador: models.Usuario = Depends(
        require_system_role("administrador")
    )
):

    db_usuario = models.Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=get_password_hash(usuario.senha),
        perfil_sistema=usuario.perfil_sistema,
        ativo=True
    )

    db.add(db_usuario)

    try:
        db.flush()

        if usuario.perfil_sistema in ("suporte_n1", "suporte_n2"):
            db.add(models.AtendenteConfig(usuario_id=db_usuario.id))

        db.commit()
        db.refresh(db_usuario)

        return db_usuario

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
<<<<<<< HEAD
            detail="Este e-mail jÃ¡ estÃ¡ cadastrado."
=======
            detail="Este e-mail já está cadastrado."
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        )


@app.get(
    "/usuarios/",
    response_model=list[schemas.UsuarioResponse]
)
def listar_usuarios(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    administrador: models.Usuario = Depends(
        require_system_role("administrador")
    )
):

    return (
        db.query(models.Usuario)
        .order_by(models.Usuario.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


# =========================================================
# GESTAO DA EQUIPE DE SUPORTE N1 / N2
# =========================================================

@app.get(
    "/equipe/",
    response_model=list[schemas.AtendenteResponse]
)
def listar_equipe(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(
        require_system_role("administrador", "suporte_n1", "suporte_n2")
    )
):
    registros = (
        db.query(models.Usuario, models.AtendenteConfig)
        .join(
            models.AtendenteConfig,
            models.AtendenteConfig.usuario_id == models.Usuario.id
        )
        .filter(
            models.Usuario.perfil_sistema.in_(("suporte_n1", "suporte_n2"))
        )
        .order_by(models.Usuario.perfil_sistema, models.Usuario.nome)
        .all()
    )

    return [
        schemas.AtendenteResponse(
            usuario_id=usuario.id,
            nome=usuario.nome,
            email=usuario.email,
            perfil_sistema=usuario.perfil_sistema,
            ativo=usuario.ativo,
            disponivel=config.disponivel,
            capacidade_maxima=config.capacidade_maxima,
            atualizado_em=config.atualizado_em,
        )
        for usuario, config in registros
    ]


@app.patch(
    "/equipe/{usuario_id}",
    response_model=schemas.AtendenteResponse
)
def atualizar_atendente(
    usuario_id: int,
    dados: schemas.AtendenteUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    alteracoes = dados.model_dump(exclude_unset=True, exclude_none=True)

    if not alteracoes:
        raise HTTPException(
            status_code=422,
            detail="Informe a disponibilidade ou a capacidade que deseja alterar."
        )

    administrador = current_user.perfil_sistema == "administrador"

    if not administrador:
        if current_user.id != usuario_id:
            raise HTTPException(
                status_code=403,
<<<<<<< HEAD
                detail="VocÃª sÃ³ pode alterar sua prÃ³pria disponibilidade."
=======
                detail="Você só pode alterar sua própria disponibilidade."
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
            )

        if set(alteracoes) - {"disponivel"}:
            raise HTTPException(
                status_code=403,
                detail="Somente o administrador pode alterar a capacidade dos atendentes."
            )

        if current_user.perfil_sistema not in ("suporte_n1", "suporte_n2"):
            raise HTTPException(
                status_code=403,
<<<<<<< HEAD
                detail="Perfil sem permissÃ£o para gerenciar disponibilidade."
=======
                detail="Perfil sem permissão para gerenciar disponibilidade."
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
            )

    usuario = (
        db.query(models.Usuario)
        .filter(models.Usuario.id == usuario_id)
        .first()
    )

    if usuario is None or usuario.perfil_sistema not in ("suporte_n1", "suporte_n2"):
<<<<<<< HEAD
        raise HTTPException(status_code=404, detail="Atendente nÃ£o encontrado.")
=======
        raise HTTPException(status_code=404, detail="Atendente não encontrado.")
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806

    if alteracoes.get("disponivel") is True and not usuario.ativo:
        raise HTTPException(
            status_code=409,
<<<<<<< HEAD
            detail="Uma conta inativa nÃ£o pode ficar disponÃ­vel para receber chamados."
=======
            detail="Uma conta inativa não pode ficar disponível para receber chamados."
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        )

    config = (
        db.query(models.AtendenteConfig)
        .filter(models.AtendenteConfig.usuario_id == usuario_id)
        .with_for_update()
        .first()
    )

    if config is None:
        config = models.AtendenteConfig(usuario_id=usuario_id)
        db.add(config)
        db.flush()

    for campo, valor in alteracoes.items():
        setattr(config, campo, valor)

    db.commit()
    db.refresh(config)

    return schemas.AtendenteResponse(
        usuario_id=usuario.id,
        nome=usuario.nome,
        email=usuario.email,
        perfil_sistema=usuario.perfil_sistema,
        ativo=usuario.ativo,
        disponivel=config.disponivel,
        capacidade_maxima=config.capacidade_maxima,
        atualizado_em=config.atualizado_em,
    )


# =========================================================
# VINCULOS ENTRE USUARIOS E FRANQUIAS
# =========================================================

@app.post(
    "/usuarios/{usuario_id}/franquias",
    response_model=schemas.UsuarioFranquiaResponse
)
def vincular_usuario_franquia(
    usuario_id: int,
    vinculo: schemas.UsuarioFranquiaCreate,
    db: Session = Depends(get_db),
    administrador: models.Usuario = Depends(
        require_system_role("administrador")
    )
):

    usuario = db.get(models.Usuario, usuario_id)

    if not usuario:
        raise HTTPException(
            status_code=404,
<<<<<<< HEAD
            detail="UsuÃ¡rio nÃ£o encontrado."
=======
            detail="Usuário não encontrado."
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        )

    if not usuario.ativo:
        raise HTTPException(
            status_code=409,
<<<<<<< HEAD
            detail="NÃ£o Ã© possÃ­vel vincular um usuÃ¡rio inativo."
=======
            detail="Não é possível vincular um usuário inativo."
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        )

    if usuario.perfil_sistema is not None:
        raise HTTPException(
            status_code=409,
<<<<<<< HEAD
            detail="Contas administrativas nÃ£o recebem papel por franquia."
=======
            detail="Contas administrativas não recebem papel por franquia."
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        )

    franquia = verificar_franquia_ativa(
        db,
        vinculo.franquia_id
    )

    existente = (
        db.query(models.UsuarioFranquia)
        .filter(
            models.UsuarioFranquia.usuario_id == usuario_id,
            models.UsuarioFranquia.franquia_id == franquia.id
        )
        .first()
    )

    if existente and existente.ativo:
        raise HTTPException(
            status_code=409,
<<<<<<< HEAD
            detail="Este usuÃ¡rio jÃ¡ possui vÃ­nculo ativo com a franquia."
=======
            detail="Este usuário já possui vínculo ativo com a franquia."
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        )

    if existente:
        existente.papel = vinculo.papel
        existente.ativo = True
        db_vinculo = existente

    else:
        db_vinculo = models.UsuarioFranquia(
            usuario_id=usuario_id,
            franquia_id=franquia.id,
            papel=vinculo.papel,
            ativo=True
        )

        db.add(db_vinculo)

    try:
        db.commit()
        db.refresh(db_vinculo)

        return db_vinculo

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
<<<<<<< HEAD
            detail="NÃ£o foi possÃ­vel criar o vÃ­nculo."
=======
            detail="Não foi possível criar o vínculo."
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        )


@app.delete(
    "/usuarios/{usuario_id}/franquias/{franquia_id}",
    response_model=schemas.UsuarioFranquiaResponse
)
def desativar_vinculo(
    usuario_id: int,
    franquia_id: int,
    db: Session = Depends(get_db),
    administrador: models.Usuario = Depends(
        require_system_role("administrador")
    )
):

    vinculo = (
        db.query(models.UsuarioFranquia)
        .filter(
            models.UsuarioFranquia.usuario_id == usuario_id,
            models.UsuarioFranquia.franquia_id == franquia_id
        )
        .first()
    )

    if not vinculo:
        raise HTTPException(
            status_code=404,
<<<<<<< HEAD
            detail="VÃ­nculo nÃ£o encontrado."
=======
            detail="Vínculo não encontrado."
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        )

    vinculo.ativo = False

    db.commit()
    db.refresh(vinculo)

    return vinculo


# =========================================================
# FRANQUIAS
# =========================================================

@app.get(
    "/franquias/",
    response_model=list[schemas.FranquiaResponse]
)
def listar_franquias(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):

    query = db.query(models.Franquia)

    if current_user.perfil_sistema not in (
        "administrador",
        "suporte_n1",
        "suporte_n2"
    ):

        query = (
            query.join(
                models.UsuarioFranquia,
                models.UsuarioFranquia.franquia_id == models.Franquia.id
            )
            .filter(
                models.UsuarioFranquia.usuario_id == current_user.id,
                models.UsuarioFranquia.ativo.is_(True),
                models.Franquia.ativa.is_(True)
            )
        )

    return (
        query.order_by(models.Franquia.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@app.post(
    "/franquias/",
    response_model=schemas.FranquiaResponse,
    status_code=201
)
def criar_franquia(
    franquia: schemas.FranquiaCreate,
    db: Session = Depends(get_db),
    administrador: models.Usuario = Depends(
        require_system_role("administrador")
    )
):

    db_franquia = models.Franquia(
        **franquia.model_dump()
    )

    db.add(db_franquia)

    try:
        db.commit()
        db.refresh(db_franquia)

        return db_franquia

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
<<<<<<< HEAD
            detail="Este telefone jÃ¡ pertence a outra franquia."
=======
            detail="Este telefone já pertence a outra franquia."
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        )


# =========================================================
# TICKETS
# =========================================================

@app.post(
    "/tickets/",
    response_model=schemas.TicketResponse,
    status_code=201
)
def criar_ticket(
    ticket: schemas.TicketCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):

    verificar_franquia_ativa(db, ticket.franquia_id)

    get_franchise_role(
        db,
        current_user,
        ticket.franquia_id
    )

    db_ticket = models.Ticket(
        **ticket.model_dump()
    )

    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)

    return db_ticket


@app.get(
    "/tickets/",
    response_model=list[schemas.TicketResponse]
)
def listar_tickets(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    franquia_id: Optional[int] = Query(default=None, gt=0),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):

    query = db.query(models.Ticket)

    if current_user.perfil_sistema not in (
        "administrador",
        "suporte_n1",
        "suporte_n2"
    ):

        franquias_autorizadas = (
            db.query(models.UsuarioFranquia.franquia_id)
            .join(
                models.Franquia,
                models.UsuarioFranquia.franquia_id == models.Franquia.id
            )
            .filter(
                models.UsuarioFranquia.usuario_id == current_user.id,
                models.UsuarioFranquia.ativo.is_(True),
                models.Franquia.ativa.is_(True)
            )
        )

        query = query.filter(
            models.Ticket.franquia_id.in_(franquias_autorizadas)
        )

    if franquia_id is not None:

        get_franchise_role(
            db,
            current_user,
            franquia_id
        )

        query = query.filter(
            models.Ticket.franquia_id == franquia_id
        )

    return (
        query.order_by(
            models.Ticket.criado_em.desc(),
            models.Ticket.id.desc()
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


@app.patch(
    "/tickets/{ticket_id}",
    response_model=schemas.TicketResponse
)
def atualizar_ticket(
    ticket_id: int,
    ticket_update: schemas.TicketUpdate,
<<<<<<< HEAD
    background_tasks: BackgroundTasks,
=======
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):

    db_ticket = obter_ticket(db, ticket_id)

    papel = verificar_acesso_ticket(
        db,
        current_user,
        db_ticket
    )

    update_data = ticket_update.model_dump(
        exclude_unset=True,
        exclude_none=True
    )

    system_user = papel in (
        "administrador",
        "suporte_n1",
        "suporte_n2"
    )

    if not system_user:

        if papel not in ("proprietario", "gerente"):
            raise HTTPException(
                status_code=403,
<<<<<<< HEAD
                detail="Seu papel nÃ£o permite alterar este chamado."
=======
                detail="Seu papel não permite alterar este chamado."
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
            )

        if "status" in update_data:
            raise HTTPException(
                status_code=403,
                detail="Somente o suporte pode alterar o status."
            )

        if db_ticket.status != "Aberto":
            raise HTTPException(
                status_code=409,
                detail="Somente chamados abertos podem ser editados pela franquia."
            )

    for campo, valor in update_data.items():
        setattr(db_ticket, campo, valor)

    db.commit()
    db.refresh(db_ticket)

<<<<<<< HEAD
    background_tasks.add_task(
        manager.broadcast,
        ticket_id,
        {
            "type": "ticket_updated",
            "ticket_id": db_ticket.id,
            "status": db_ticket.status,
        }
    )

=======
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
    return db_ticket


# =========================================================
# MENSAGENS E ANEXOS
# =========================================================

@app.post(
    "/tickets/{ticket_id}/mensagens/",
    response_model=schemas.MensagemResponse,
    status_code=201
)
async def enviar_mensagem(
    ticket_id: int,
    texto: Optional[str] = Form(default=None),
    file: Optional[UploadFile] = File(default=None),
<<<<<<< HEAD
    interna: bool = Form(default=False),
=======
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):

    ticket = obter_ticket(db, ticket_id)

    verificar_acesso_ticket(
        db,
        current_user,
        ticket
    )

<<<<<<< HEAD
    papel = verificar_acesso_ticket(
        db,
        current_user,
        ticket
    )

    equipe_suporte = papel in ("administrador", "suporte_n1", "suporte_n2")

    if interna and not equipe_suporte:
        raise HTTPException(
            status_code=403,
            detail="Apenas a equipe de suporte pode criar notas internas.",
        )
=======
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
    if not (texto and texto.strip()) and file is None:
        raise HTTPException(
            status_code=400,
            detail="Informe um texto ou anexe uma imagem."
        )

    anexo_url = None
    caminho_salvo = None

    try:

        if file is not None:

            conteudo = await file.read(
                MAX_UPLOAD_BYTES + 1
            )

            if len(conteudo) > MAX_UPLOAD_BYTES:
                raise HTTPException(
                    status_code=413,
                    detail="O arquivo ultrapassa o limite de 20 MB."
                )

            extensao = detectar_imagem(conteudo)

            if extensao is None:
                raise HTTPException(
                    status_code=415,
<<<<<<< HEAD
                    detail="Formato nÃ£o permitido. Utilize JPG, PNG ou WEBP."
=======
                    detail="Formato não permitido. Utilize JPG, PNG ou WEBP."
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
                )

            nome_seguro = f"{uuid.uuid4().hex}.{extensao}"

            caminho_salvo = UPLOAD_DIR / nome_seguro

            caminho_salvo.write_bytes(conteudo)

            anexo_url = f"/uploads/{nome_seguro}"

        db_mensagem = models.Mensagem(
            ticket_id=ticket_id,
            remetente_id=current_user.id,
            remetente=current_user.nome,
            texto=texto.strip() if texto else None,
<<<<<<< HEAD
            url_anexo=anexo_url,
            interna=interna
=======
            url_anexo=anexo_url
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        )

        db.add(db_mensagem)
        db.commit()
        db.refresh(db_mensagem)

    except HTTPException:
        db.rollback()
        if caminho_salvo and caminho_salvo.exists():
            caminho_salvo.unlink()
        raise

    except Exception:
        db.rollback()

        if caminho_salvo and caminho_salvo.exists():
            caminho_salvo.unlink()

        logger.exception("Erro ao registrar mensagem.")

        raise HTTPException(
            status_code=500,
<<<<<<< HEAD
            detail="NÃ£o foi possÃ­vel registrar a mensagem."
=======
            detail="Não foi possível registrar a mensagem."
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        )

    finally:
        if file is not None:
            await file.close()

    await manager.broadcast(
        ticket_id,
        {
            "type": "new_message",
<<<<<<< HEAD
              "interna": db_mensagem.interna,
=======
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
            "id": db_mensagem.id,
            "ticket_id": ticket_id,
            "remetente": current_user.nome,
            "remetente_id": current_user.id,
            "texto": db_mensagem.texto,
            "url_anexo": db_mensagem.url_anexo,
            "criada_em": db_mensagem.criada_em.isoformat()
        }
    )

    return db_mensagem


@app.get(
    "/tickets/{ticket_id}/mensagens/",
    response_model=list[schemas.MensagemResponse]
)
def listar_mensagens(
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

<<<<<<< HEAD
    equipe_suporte = current_user.perfil_sistema in (
        "administrador",
        "suporte_n1",
        "suporte_n2",
    )

    query = db.query(models.Mensagem).filter(
        models.Mensagem.ticket_id == ticket_id
    )

    if not equipe_suporte:
        query = query.filter(models.Mensagem.interna == False)

    return query.order_by(models.Mensagem.id.asc()).all()

=======
    return (
        db.query(models.Mensagem)
        .filter(models.Mensagem.ticket_id == ticket_id)
        .order_by(models.Mensagem.id.asc())
        .all()
    )

>>>>>>> 16f2a51bb3087317222397def353d27e75b44806

# =========================================================
# ANEXOS PRIVADOS - ACESSO AUTENTICADO
# =========================================================

@app.get("/uploads/{filename}")
def obter_anexo(
    filename: str,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):

    if (
        not filename
        or filename in (".", "..")
        or "/" in filename
        or "\\" in filename
        or "\x00" in filename
    ):
        raise HTTPException(
            status_code=404,
<<<<<<< HEAD
            detail="Anexo nÃ£o encontrado."
=======
            detail="Anexo não encontrado."
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        )

    url_anexo = f"/uploads/{filename}"

    mensagem = (
        db.query(models.Mensagem)
        .join(
            models.Ticket,
            models.Mensagem.ticket_id == models.Ticket.id
        )
        .filter(models.Mensagem.url_anexo == url_anexo)
        .first()
    )

    if mensagem is None:
        raise HTTPException(
            status_code=404,
<<<<<<< HEAD
            detail="Anexo nÃ£o encontrado."
=======
            detail="Anexo não encontrado."
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        )

    ticket = obter_ticket(db, mensagem.ticket_id)

    verificar_acesso_ticket(
        db,
        current_user,
        ticket
    )

    extensao = Path(filename).suffix.lower().lstrip(".")

    media_type = IMAGE_FORMATS.get(extensao)

    if media_type is None:
        raise HTTPException(
            status_code=415,
<<<<<<< HEAD
            detail="Formato de anexo nÃ£o permitido."
=======
            detail="Formato de anexo não permitido."
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        )

    caminho = (UPLOAD_DIR / filename).resolve()

    if caminho.parent != UPLOAD_DIR.resolve() or not caminho.is_file():
        raise HTTPException(
            status_code=404,
<<<<<<< HEAD
            detail="Arquivo nÃ£o encontrado."
=======
            detail="Arquivo não encontrado."
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        )

    return FileResponse(
        path=caminho,
        media_type=media_type,
        headers={
            "Cache-Control": "private, no-store"
        }
    )


# =========================================================
# EMISSAO DE TOKEN PARA WEBSOCKET
# =========================================================

@app.post(
    "/tickets/{ticket_id}/ws-token",
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
        "token": token,
        "token_type": "websocket",
<<<<<<< HEAD
        "expires_in": WEBSOCKET_TOKEN_EXPIRE_SECONDS,
        "pode_criar_nota_interna": pode_criar_nota_interna(current_user)
=======
        "expires_in": WEBSOCKET_TOKEN_EXPIRE_SECONDS
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
    }


# =========================================================
# WEBSOCKET AUTENTICADO
# =========================================================

@app.websocket("/ws/tickets/{ticket_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    ticket_id: int
):

    connected = False

<<<<<<< HEAD
    # Somente o frontend publicado pode iniciar a conexÃ£o.
=======
    # Somente o frontend publicado pode iniciar a conexão.
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
    origin = websocket.headers.get("origin")

    if origin not in FRONTEND_ORIGINS:
        await websocket.close(code=1008)
        return

    await websocket.accept()

    try:

<<<<<<< HEAD
        # O token vai no primeiro frame, nÃ£o na URL.
        # Isso evita exposiÃ§Ã£o em logs de proxy e navegador.
=======
        # O token vai no primeiro frame, não na URL.
        # Isso evita exposição em logs de proxy e navegador.
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        handshake = await asyncio.wait_for(
            websocket.receive_json(),
            timeout=5
        )

        if (
            not isinstance(handshake, dict)
            or handshake.get("type") != "authenticate"
            or not isinstance(handshake.get("token"), str)
        ):
            await websocket.close(code=1008)
            return

        payload = decode_websocket_token(
            handshake["token"]
        )

        token_ticket_id = int(payload["ticket_id"])
        user_id = int(payload["sub"])

        if token_ticket_id != ticket_id:
            await websocket.close(code=1008)
            return

<<<<<<< HEAD
        # Valida identidade, estado e autorizaÃ§Ã£o no PostgreSQL.
=======
        # Valida identidade, estado e autorização no PostgreSQL.
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
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

<<<<<<< HEAD
            # Determine if user is support staff for internal note filtering
            is_support = user.perfil_sistema in ("administrador", "suporte_n1", "suporte_n2")

=======
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        finally:
            db.close()

        manager.connect(
            ticket_id,
<<<<<<< HEAD
            websocket,
            is_support=is_support
=======
            websocket
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        )

        connected = True

        await websocket.send_json(
            {
                "type": "authenticated",
                "ticket_id": ticket_id
            }
        )

<<<<<<< HEAD
        # O WebSocket Ã© destinado Ã  recepÃ§Ã£o de eventos.
=======
        # O WebSocket é destinado à recepção de eventos.
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        # Novas mensagens devem ser gravadas pela API REST.
        while True:

            data = await websocket.receive_text()

            if data == "ping":
                await websocket.send_json(
                    {"type": "pong"}
                )

            else:
                await websocket.send_json(
                    {
                        "type": "error",
                        "detail": "Envie mensagens pela API REST."
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
<<<<<<< HEAD
        logger.exception("Erro na conexÃ£o WebSocket.")
=======
        logger.exception("Erro na conexão WebSocket.")
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
        await websocket.close(code=1011)

    finally:

        if connected:
            manager.disconnect(ticket_id, websocket)
<<<<<<< HEAD

=======
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
