
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    CheckConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class Franquia(Base):
    __tablename__ = "franquias"

    id = Column(Integer, primary_key=True)
    nome_responsavel = Column(String, index=True)
    unidade = Column(String, index=True)
    telefone = Column(String, unique=True, index=True)
    ativa = Column(Boolean, default=True)
    criada_em = Column(DateTime(timezone=True), server_default=func.now())

    tickets = relationship(
        "Ticket",
        back_populates="franquia"
    )

    usuarios = relationship(
        "UsuarioFranquia",
        back_populates="franquia",
        cascade="all, delete-orphan"
    )


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    franquia_id = Column(Integer, ForeignKey("franquias.id"))
    descricao = Column(Text)
    status = Column(String, default="Aberto")
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    franquia = relationship(
        "Franquia",
        back_populates="tickets"
    )

    usuario = relationship(
        "Usuario",
        back_populates="tickets_abertos"
    )

    mensagens = relationship(
        "Mensagem",
        back_populates="ticket"
    )


class Mensagem(Base):
    __tablename__ = "mensagens"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    remetente = Column(String)
    remetente_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    texto = Column(Text, nullable=True)
    url_anexo = Column(String, nullable=True)
    interna = Column(Boolean, default=False, server_default="false", nullable=False)

    ticket = relationship(
        "Ticket",
        back_populates="mensagens"
    )


# =========================================================
# USUARIOS DO SISTEMA
# =========================================================

class Usuario(Base):
    __tablename__ = "usuarios"

    __table_args__ = (
        CheckConstraint(
            "perfil_sistema IS NULL OR "
            "perfil_sistema IN ('administrador', 'suporte_n1', 'suporte_n2')",
            name="ck_usuarios_perfil_sistema"
        ),
    )

    id = Column(Integer, primary_key=True)

    nome = Column(String(150), nullable=False)

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    senha_hash = Column(String(255), nullable=False)

    # Administrador e suporte têm perfil no sistema.
    # Franqueados e funcionários possuem papel por unidade.
    perfil_sistema = Column(String(30), nullable=True)

    ativo = Column(Boolean, default=True, nullable=False)

    criado_em = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    franquias = relationship(
        "UsuarioFranquia",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )

    tickets_abertos = relationship(
        "Ticket",
        back_populates="usuario",
        foreign_keys="Ticket.usuario_id"
    )


# =========================================================
# CONFIGURACAO INDIVIDUAL DOS ATENDENTES
# =========================================================

class AtendenteConfig(Base):
    __tablename__ = "atendente_config"

    __table_args__ = (
        CheckConstraint(
            "capacidade_maxima >= 1",
            name="ck_atendente_config_capacidade_maxima"
        ),
    )

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        primary_key=True
    )

    disponivel = Column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False
    )

    capacidade_maxima = Column(
        Integer,
        default=10,
        server_default="10",
        nullable=False
    )

    atualizado_em = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


# =========================================================
# VINCULO ENTRE USUARIOS E FRANQUIAS (N:N)
# =========================================================

class UsuarioFranquia(Base):
    __tablename__ = "usuario_franquias"

    __table_args__ = (
        CheckConstraint(
            "papel IN ('proprietario', 'gerente', 'funcionario')",
            name="ck_usuario_franquias_papel"
        ),
    )

    # Chave composta: impede vínculo duplicado.
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        primary_key=True
    )

    franquia_id = Column(
        Integer,
        ForeignKey("franquias.id", ondelete="CASCADE"),
        primary_key=True,
        index=True
    )

    papel = Column(String(30), nullable=False)

    ativo = Column(Boolean, default=True, nullable=False)

    criado_em = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    usuario = relationship(
        "Usuario",
        back_populates="franquias"
    )

    franquia = relationship(
        "Franquia",
        back_populates="usuarios"
    )
