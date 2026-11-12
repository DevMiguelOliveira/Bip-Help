
from getpass import getpass

from sqlalchemy.exc import IntegrityError

from auth import get_password_hash
from database import SessionLocal
from models import Usuario


def main():

    db = SessionLocal()

    try:
        admin_existente = (
            db.query(Usuario)
            .filter(
                Usuario.perfil_sistema == "administrador"
            )
            .first()
        )

        if admin_existente:
            print("Já existe um administrador cadastrado.")
            print("Operação cancelada.")
            return

        print("===== PRIMEIRO ADMINISTRADOR BIPMANAGER =====")

        nome = input("Nome completo: ").strip()
        email = input("E-mail: ").strip().lower()

        if not nome or not email or "@" not in email:
            print("Nome ou e-mail inválido.")
            return

        senha = getpass("Crie uma senha (mínimo 14 caracteres): ")
        confirmacao = getpass("Confirme a senha: ")

        if len(senha) < 14:
            print("A senha precisa ter pelo menos 14 caracteres.")
            return

        if senha != confirmacao:
            print("As senhas não correspondem.")
            return

        usuario = Usuario(
            nome=nome,
            email=email,
            senha_hash=get_password_hash(senha),
            perfil_sistema="administrador",
            ativo=True,
        )

        db.add(usuario)
        db.commit()
        db.refresh(usuario)

        print("\nADMINISTRADOR CRIADO COM SUCESSO.")
        print("ID:", usuario.id)
        print("E-mail:", usuario.email)
        print("Senha: não exibida.")

    except IntegrityError:
        db.rollback()
        print("Erro: este e-mail já está cadastrado.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
