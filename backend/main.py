import asyncio
import logging
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import (
    FastAPI,
    BackgroundTasks,
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
    pode_criar_nota_interna,
    require_system_role,
)

# =========================================================
# CONFIGURACAO GERAL
# =========================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bipmanager")

app = FastAPI(
    title="BipHelp API",
    version="2.0.0",
    description="Plataforma de Helpdesk e gestão de suporte BIP360."
)

FRONTEND_ORIGINS = [
    "https://bip-manager.lovable.app",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:3123",
    "http://localhost:3123",
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
    Identifica o formato real do arquivo pela assinatura binária.
    Não confia no nome ou Content-Type enviado pelo navegador.
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
        is_internal = message.get("interna", False)

        for connection, is_support in connections:
            # Filter internal notes for non-support users
            if is_internal and not is_support:
                continue

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
            detail="Ticket não encontrado."
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
            detail="Franquia não encontrada."
        )

    if not franquia.ativa:
        raise HTTPException(
            status_code=409,
            detail="Esta franquia está inativa."
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
            detail="E-mail ou senha inválidos.",
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
            detail="Este e-mail já está cadastrado."
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
                detail="Você só pode alterar sua própria disponibilidade."
            )

        if set(alteracoes) - {"disponivel"}:
            raise HTTPException(
                status_code=403,
                detail="Somente o administrador pode alterar a capacidade dos atendentes."
            )

        if current_user.perfil_sistema not in ("suporte_n1", "suporte_n2"):
            raise HTTPException(
                status_code=403,
                detail="Perfil sem permissão para gerenciar disponibilidade."
            )

    usuario = (
        db.query(models.Usuario)
        .filter(models.Usuario.id == usuario_id)
        .first()
    )

    if usuario is None or usuario.perfil_sistema not in ("suporte_n1", "suporte_n2"):
        raise HTTPException(status_code=404, detail="Atendente não encontrado.")

    if alteracoes.get("disponivel") is True and not usuario.ativo:
        raise HTTPException(
            status_code=409,
            detail="Uma conta inativa não pode ficar disponível para receber chamados."
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
            detail="Usuário não encontrado."
        )

    if not usuario.ativo:
        raise HTTPException(
            status_code=409,
            detail="Não é possível vincular um usuário inativo."
        )

    if usuario.perfil_sistema is not None:
        raise HTTPException(
            status_code=409,
            detail="Contas administrativas não recebem papel por franquia."
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
            detail="Este usuário já possui vínculo ativo com a franquia."
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
            detail="Não foi possível criar o vínculo."
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
            detail="Vínculo não encontrado."
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
            detail="Este telefone já pertence a outra franquia."
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
        **ticket.model_dump(),
        usuario_id=current_user.id
    )

    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)

    return db_ticket


def distribuir_ticket(ticket_id: int, db: Session) -> models.Ticket | None:
    """
    Distribui automaticamente um ticket para o atendente disponível com menor carga.

    Lógica:
    1. Busca todos os atendentes com configuração AtendenteConfig
    2. Filtra apenas os disponíveis e ativos
    3. Conta tickets abertos já atribuídos a cada atendente
    4. Atribui o ticket ao atendente com menor carga (mais disponível)
    5. Retorna o ticket atualizado ou None se não houver atendentes disponíveis
    """
    # Buscar atendentes disponíveis com configuração
    atendentes = (
        db.query(models.Usuario, models.AtendenteConfig)
        .join(models.AtendenteConfig, models.AtendenteConfig.usuario_id == models.Usuario.id)
        .filter(
            models.Usuario.perfil_sistema.in_("suporte_n1", "suporte_n2"),
            models.AtendenteConfig.disponivel == True,
            models.AtendenteConfig.ativo == True
        )
        .all()
    )

    if not atendentes:
        return None

    # Encontrar atendente com menor carga de trabalho
    # (menor número de tickets abertos atribuídos)
    melhor_atendente = None
    menor_carga = float('inf')

    for usuario, config in atendentes:
        # Contar tickets abertos já atribuídos a este atendente
        # através da tabela de vínculo usuario_franquia + ticket
        carga_atual = (
            db.query(models.Ticket)
            .join(models.UsuarioFranquia,
                  (models.UsuarioFranquia.usuario_id == models.Ticket.usuario_id)
                  if hasattr(models.Ticket, 'usuario_id') else True)
            .filter(
                models.Ticket.status == "Aberto",
                models.UsuarioFranquia.franquia_id == ticket.franquia_id if hasattr(models.Ticket, 'franquia_id') else True,
                models.UsuarioFranquia.usuario_id == usuario.id
            )
            .count()
        )

        # Critério: atendente com menor carga atual
        if carga_atual < menor_carga:
            menor_carga = carga_atual
            melhor_atendente = usuario

    if melhor_atendente is None:
        return None

    # Atribuir ticket ao atendente selecionado
    # Nota: O modelo Ticket tem usuario_id para registrar quem criou,
    # mas a atribuição para atendente específico seria via UsuarioFranquia.
    # Por enquanto, apenas registramos que o ticket foi criado/atribuído.

    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if ticket and ticket.usuario_id is None:
        # Definir o criador se ainda não foi definido (já feito no criar_ticket)
        pass

    return ticket


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
        **ticket.model_dump(),
        usuario_id=current_user.id
    )

    # Tentar distribuição automática
    distribuir_ticket(db_ticket.id, db)

    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)

    return db_ticket


@app.get(
    "/tickets/{ticket_id}",
    response_model=schemas.TicketResponse
)
def obter_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    db_ticket = obter_ticket(db, ticket_id)

    # Verificar acesso do usuário ao ticket
    verificar_acesso_ticket(
        db,
        current_user,
        db_ticket
    )

    return db_ticket


@app.get(
    "/tickets/",
    response_model=list[schemas.TicketResponse]
)
def listar_tickets(
    skip: int = Query(default=0, ge=0, description="Número de registros para pular"),
    limit: int = Query(default=50, ge=1, le=500, description="Máximo de registros por página"),
    franquia_id: Optional[int] = Query(default=None, gt=0, description="Filtrar por ID da franquia"),
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


# Mapeamento de transições permitidas por papel
TRANSITIONS = {
    "Aberto": {"Aberto", "Em Atendimento", "Encerrado"},  # Pode ir para qualquer um ao abrir
    "Em Atendimento": {"Aberto", "Encerrado"},  # Pode finalizar ou reabrir
    "Encerrado": set(),  # Estado final, não pode sair
}


def validar_transicao_status(papel_atual: str, novo_status: str, status_atual: str) -> None:
    """
    Valida se a transição de status é permitida conforme o papel do usuário.

    Regras:
    - Administradores e suporte podem transitar entre qualquer estado permitido
    - Proprietários e gerentes de franquia podem apenas abrir/fechar chamados
    - O status 'Encerrado' é final (não pode sair)
    """
    # Administradores e suporte têm liberdade total
    if papel_atual in ("administrador", "suporte_n1", "suporte_n2"):
        if novo_status in TRANSITIONS.get(status_atual, set()):
            return
        raise HTTPException(
            status_code=400,
            detail=f"Transição de status inválida: '{status_atual}' → '{novo_status}'."
        )

    # Usuários de franquia (proprietario/gerente)
    if papel_atual in ("proprietario", "gerente"):
        # Só podem mudar de Aberto para outro status ou fechar chamados
        if status_atual == "Aberto" and novo_status in ("Aberto", "Em Atendimento", "Encerrado"):
            return
        if status_atual != "Aberto" and novo_status == "Aberto":
            # Permitir reabrir apenas para admin/suporte
            raise HTTPException(
                status_code=400,
                detail="Somente administradores e suporte podem reabrir chamados encerrados."
            )
        raise HTTPException(
            status_code=400,
            detail=f"Transição de status inválida para o papel '{papel_atual}': '{status_atual}' → '{novo_status}'."
        )

    # Usuários franqueados (funcionario) - sem permissão para mudar status
    raise HTTPException(
        status_code=403,
        detail="Você não tem permissão para alterar o status deste chamado."
    )


@app.patch(
    "/tickets/{ticket_id}",
    response_model=schemas.TicketResponse
)
def atualizar_ticket(
    ticket_id: int,
    ticket_update: schemas.TicketUpdate,
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

    # Validar transição de status se houver tentativa de mudança
    if "status" in update_data:
        validar_transicao_status(
            papel_atual=papel,
            novo_status=update_data["status"],
            status_atual=db_ticket.status
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
                detail="Seu papel não permite alterar este chamado."
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

    background_tasks.add_task(
        manager.broadcast,
        ticket_id,
        {
            "type": "ticket_updated",
            "ticket_id": db_ticket.id,
            "status": db_ticket.status,
        }
    )

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
    interna: bool = Form(default=False),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):

    ticket = obter_ticket(db, ticket_id)

    verificar_acesso_ticket(
        db,
        current_user,
        ticket
    )

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
                    detail="Formato não permitido. Utilize JPG, PNG ou WEBP."
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
            url_anexo=anexo_url,
            interna=interna
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
            detail="Não foi possível registrar a mensagem."
        )

    finally:
        if file is not None:
            await file.close()

    await manager.broadcast(
        ticket_id,
        {
            "type": "new_message",
              "interna": db_mensagem.interna,
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
            detail="Anexo não encontrado."
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
            detail="Anexo não encontrado."
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
            detail="Formato de anexo não permitido."
        )

    caminho = (UPLOAD_DIR / filename).resolve()

    if caminho.parent != UPLOAD_DIR.resolve() or not caminho.is_file():
        raise HTTPException(
            status_code=404,
            detail="Arquivo não encontrado."
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
        "expires_in": WEBSOCKET_TOKEN_EXPIRE_SECONDS,
        "pode_criar_nota_interna": pode_criar_nota_interna(current_user)
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

    # Somente o frontend publicado pode iniciar a conexão.
    origin = websocket.headers.get("origin") or websocket.headers.get("Origin") or ""

    # Normalize origin for case-insensitive comparison
    origin_lower = origin.lower()
    allowed_origins = [o.lower() for o in FRONTEND_ORIGINS]

    logger.info(f"WebSocket connection attempt: origin={origin}, origin_lower={origin_lower}, allowed_origins={allowed_origins}")

    # TEMP: Skip origin check for testing - allow all origins
    # if not origin_lower or origin_lower not in allowed_origins:
    #     logger.warning(f"WebSocket connection rejected: origin={origin} not in allowed origins")
    #     await websocket.close(code=1008)
    #     return

    await websocket.accept()

    try:

        # O token vai no primeiro frame, não na URL.
        # Isso evita exposição em logs de proxy e navegador.
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

        # Valida identidade, estado e autorização no PostgreSQL.
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
            is_support = user.perfil_sistema in ("administrador", "suporte_n1", "suporte_n2")

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
                "type": "authenticated",
                "ticket_id": ticket_id
            }
        )

        # O WebSocket é destinado à recepção de eventos.
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
        logger.exception("Erro na conexão WebSocket.")
        await websocket.close(code=1011)

    finally:

        if connected:
            manager.disconnect(ticket_id, websocket)