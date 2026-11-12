
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from jwt.exceptions import InvalidTokenError

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from database import SessionLocal
import models


# =========================================================
# CONFIGURACAO JWT
# =========================================================

JWT_SECRET_FILE = Path("/etc/bipmanager/jwt_secret")

if not JWT_SECRET_FILE.is_file():
    raise RuntimeError("Arquivo de assinatura JWT não encontrado.")

SECRET_KEY = JWT_SECRET_FILE.read_text().strip()

if len(SECRET_KEY) < 64:
    raise RuntimeError("Chave JWT inválida ou muito curta.")

ALGORITHM = "HS256"
JWT_ISSUER = "bipmanager"
JWT_AUDIENCE = "bipmanager-api"

ACCESS_TOKEN_EXPIRE_MINUTES = 30


# =========================================================
# HASH DE SENHAS
# =========================================================

password_hash = PasswordHash.recommended()

# Hash fictício utilizado para reduzir diferenças de tempo
# quando o e-mail informado não existe.
DUMMY_HASH = password_hash.hash(
    "BIPManager-Dummy-Password-Not-For-Login"
)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return password_hash.verify(password, hashed_password)
    except Exception:
        return False


# =========================================================
# SESSAO DO BANCO
# =========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================================================
# AUTENTICACAO DE USUARIOS
# =========================================================

def authenticate_user(
    db: Session,
    email: str,
    password: str
):
    email = email.strip().lower()

    user = (
        db.query(models.Usuario)
        .filter(models.Usuario.email == email)
        .first()
    )

    if user is None:
        verify_password(password, DUMMY_HASH)
        return None

    password_valid = verify_password(
        password,
        user.senha_hash
    )

    if not password_valid or not user.ativo:
        return None

    return user


# =========================================================
# CRIACAO DE TOKEN
# =========================================================

def create_access_token(
    user_id: int,
    expires_delta: timedelta | None = None
) -> str:

    now = datetime.now(timezone.utc)

    expiration = now + (
        expires_delta
        or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload = {
        "sub": str(user_id),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "exp": expiration,
        "token_use": "access",
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# =========================================================
# VALIDACAO DE TOKEN
# =========================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou sessão expirada.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
            options={
                "require": [
                    "exp",
                    "iat",
                    "sub",
                    "iss",
                    "aud",
                ]
            }
        )

        if payload.get("token_use") != "access":
            raise credentials_error

        user_id = int(payload["sub"])

    except (InvalidTokenError, ValueError, TypeError):
        raise credentials_error

    user = (
        db.query(models.Usuario)
        .filter(models.Usuario.id == user_id)
        .first()
    )

    if user is None or not user.ativo:
        raise credentials_error

    return user


# =========================================================
# AUTORIZACAO ADMINISTRATIVA
# =========================================================

def require_system_role(*allowed_roles):

    def role_checker(
        current_user=Depends(get_current_user)
    ):

        if current_user.perfil_sistema not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não possui permissão para esta operação."
            )

        return current_user

    return role_checker


# =========================================================
# AUTORIZACAO POR FRANQUIA
# =========================================================

def get_franchise_role(
    db: Session,
    current_user: models.Usuario,
    franquia_id: int
):

    if current_user.perfil_sistema in (
        "administrador",
        "suporte_n1",
        "suporte_n2"
    ):
        return current_user.perfil_sistema

    membership = (
        db.query(models.UsuarioFranquia)
        .join(
            models.Franquia,
            models.UsuarioFranquia.franquia_id == models.Franquia.id
        )
        .filter(
            models.UsuarioFranquia.usuario_id == current_user.id,
            models.UsuarioFranquia.franquia_id == franquia_id,
            models.UsuarioFranquia.ativo.is_(True),
            models.Franquia.ativa.is_(True),
        )
        .first()
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não possui acesso a esta franquia."
        )

    return membership.papel


def user_can_access_ticket(
    db: Session,
    current_user: models.Usuario,
    ticket: models.Ticket
) -> bool:

    try:
        get_franchise_role(
            db,
            current_user,
            ticket.franquia_id
        )
        return True

    except HTTPException:
        return False

# =========================================================
# TOKENS TEMPORARIOS PARA WEBSOCKETS
# =========================================================

WEBSOCKET_TOKEN_EXPIRE_SECONDS = 60


def create_websocket_token(
    user_id: int,
    ticket_id: int
) -> str:

    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "exp": now + timedelta(
            seconds=WEBSOCKET_TOKEN_EXPIRE_SECONDS
        ),
        "token_use": "websocket",
        "ticket_id": ticket_id,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


<<<<<<< HEAD
# =========================================================
# AUTORIZACAO DE MENSAGENS INTERNAS
# =========================================================

def check_mensagem_interna_autorizacao(
    db: Session,
    current_user: models.Usuario,
    mensagem: models.Mensagem
) -> bool:
    """
    Verifica se o usuário atual pode acessar uma mensagem interna.
    
    Regras:
    - Administradores e suporte do sistema (perfil_sistema) podem acessar.
    - Usuários com perfil de franquia (proprietario, gerente, funcionario)
      NÃO podem acessar mensagens internas de outras franquias ou da própria.
    - Apenas o criador da mensagem ou suporte de sistema tem acesso.
    
    Returns True se autorizado, False otherwise.
    """
    # Administradores e suporte do sistema têm acesso total
    if current_user.perfil_sistema in (
        "administrador",
        "suporte_n1", 
        "suporte_n2"
    ):
        return True
    
    # Usuários de franquia NÃO podem acessar mensagens internas
    # Verificar se a mensagem é interna
    if mensagem.interna:
        # Franqueados não podem ver notas internas
        return False
    
    # Mensagens normais (interna=False) podem ser acessadas conforme permissão de franquia
    return True

def pode_criar_nota_interna(current_user: models.Usuario) -> bool:
    """
    Verifica se o usuario pode criar notas internas.
    Apenas administradores e suporte do sistema podem criar notas internas.
    """
    return current_user.perfil_sistema in (
        "administrador",
        "suporte_n1",
        "suporte_n2"
    )

=======
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
def decode_websocket_token(token: str) -> dict:

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        issuer=JWT_ISSUER,
        audience=JWT_AUDIENCE,
        options={
            "require": [
                "exp",
                "iat",
                "sub",
                "iss",
                "aud",
                "ticket_id",
            ]
        }
    )

    if payload.get("token_use") != "websocket":
        raise InvalidTokenError("Token não autorizado para WebSocket.")

<<<<<<< HEAD
    return payload
=======
    return payload
>>>>>>> 16f2a51bb3087317222397def353d27e75b44806
