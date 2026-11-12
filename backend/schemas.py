from datetime import datetime
from typing import Literal

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


# =========================================================
# FRANQUIAS
# =========================================================

class FranquiaCreate(BaseModel):
    nome_responsavel: str
    unidade: str
    telefone: str


class FranquiaResponse(FranquiaCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ativa: bool


# =========================================================
# TICKETS
# =========================================================

TicketStatus = Literal["Aberto", "Em Atendimento", "Encerrado"]


class TicketCreate(BaseModel):
    franquia_id: int
    descricao: str = Field(min_length=1, max_length=10000)


class TicketUpdate(BaseModel):
    status: TicketStatus | None = None
    descricao: str | None = Field(default=None, min_length=1, max_length=10000)


class TicketResponse(TicketCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: TicketStatus
    criado_em: datetime


# =========================================================
# MENSAGENS
# =========================================================

class MensagemCreate(BaseModel):
    texto: str


class MensagemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    interna: bool = False
    criada_em: datetime


# =========================================================
# AUTENTICACAO
# =========================================================

class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


class WebSocketTokenResponse(BaseModel):
    token: str
    token_type: Literal["websocket"] = "websocket"
    expires_in: int
    pode_criar_nota_interna: bool = False


# =========================================================
# USUARIOS
# =========================================================

SystemRole = Literal["administrador", "suporte_n1", "suporte_n2"]

FranchiseRole = Literal["proprietario", "gerente", "funcionario"]


class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    email: str = Field(min_length=5, max_length=255)
    senha: str = Field(min_length=14, max_length=128)
    perfil_sistema: SystemRole | None = None

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, value):
        value = value.strip()

        if len(value) < 2:
            raise ValueError("Nome inválido.")

        return value

    @field_validator("email")
    @classmethod
    def validar_email(cls, value):
        value = value.strip().lower()

        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("Endereço de e-mail inválido.")

        return value


class UsuarioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: str
    perfil_sistema: str | None
    ativo: bool
    criado_em: datetime


class AtendenteResponse(BaseModel):
    usuario_id: int
    nome: str
    email: str
    perfil_sistema: Literal["suporte_n1", "suporte_n2"]
    ativo: bool
    disponivel: bool
    capacidade_maxima: int
    atualizado_em: datetime


class AtendenteUpdate(BaseModel):
    disponivel: bool | None = None
    capacidade_maxima: int | None = Field(default=None, ge=1)


# =========================================================
# VINCULOS USUARIO / FRANQUIA
# =========================================================

class UsuarioFranquiaCreate(BaseModel):
    franquia_id: int
    papel: FranchiseRole


class UsuarioFranquiaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    usuario_id: int
    franquia_id: int
    papel: FranchiseRole
    ativo: bool
    criado_em: datetime


class MinhaFranquiaResponse(BaseModel):
    franquia_id: int
    unidade: str
    nome_responsavel: str
    papel: FranchiseRole
    ativa: bool


class UsuarioMeResponse(UsuarioResponse):
    franquias: list[MinhaFranquiaResponse] = []
