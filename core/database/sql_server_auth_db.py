import pyodbc
import bcrypt
from datetime import datetime, timedelta
from core.utils.db_connection import get_db_connection

# --- Constantes de Autenticação ---
MAX_TENTATIVAS = 5
BLOQUEIO_MINUTOS = 15
SESSAO_MINUTOS = 30


# --- Inicialização do banco (Cria a tabela se não existir) ---
from sqlalchemy import text
import pyodbc
import bcrypt
from datetime import datetime, timedelta
from core.utils.db_connection import get_db_connection

# --- Constantes de Autenticação ---
MAX_TENTATIVAS = 5
BLOQUEIO_MINUTOS = 15
SESSAO_MINUTOS = 30


# --- Inicialização do banco (Cria a tabela se não existir) ---
def init_db():
    with get_db_connection() as conn:
        conn.execute(
            text(
                """
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='usuarios' and xtype='U')
                CREATE TABLE usuarios (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    username NVARCHAR(255) UNIQUE NOT NULL,
                    password_hash NVARCHAR(255) NOT NULL,
                    role NVARCHAR(50) NOT NULL,
                    ativo BIT DEFAULT 1,
                    tentativas_invalidas INT DEFAULT 0,
                    bloqueado_ate DATETIME,
                    ultimo_login DATETIME,
                    redefinir_solicitado BIT DEFAULT 0,
                    redefinir_aprovado BIT DEFAULT 0
                );
                """
            )
        )
        # SQLAlchemy auto-commits DDL statements, but explicit commit for safety
        # conn.commit() is not needed here as execute handles it for DDL


# --- Criação de usuário ---
def criar_usuario(username, password, role="user"):
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        with get_db_connection() as conn:
            conn.execute(
                text("INSERT INTO usuarios (username, password_hash, role) VALUES (:username, :password_hash, :role)"),
                {"username": username, "password_hash": password_hash, "role": role},
            )
            conn.commit()
    except pyodbc.IntegrityError:
        raise ValueError("Usuário já existe")






# --- Autenticação ---
def autenticar_usuario(username, password):
    with get_db_connection() as conn:
        result = conn.execute(
            text("SELECT id, password_hash, ativo, tentativas_invalidas, bloqueado_ate, role FROM usuarios WHERE username=:username"),
            {"username": username}
        ).fetchone()

        if not result:
            return None, "Usuário não encontrado"
        
        user_id, password_hash, ativo, tentativas, bloqueado_ate, role = result
        now = datetime.now()

        if not ativo:
            return None, "Usuário inativo ou bloqueado"

        if bloqueado_ate:
            if now < bloqueado_ate:
                return None, f"Usuário bloqueado até {bloqueado_ate.strftime('%Y-%m-%d %H:%M:%S')}"

        if not bcrypt.checkpw(password.encode(), password_hash.encode()):
            tentativas += 1
            if tentativas >= MAX_TENTATIVAS:
                bloqueado_ate = now + timedelta(minutes=BLOQUEIO_MINUTOS)
                conn.execute(
                    text("UPDATE usuarios SET tentativas_invalidas=:tentativas, bloqueado_ate=:bloqueado_ate WHERE id=:id"),
                    {"tentativas": tentativas, "bloqueado_ate": bloqueado_ate, "id": user_id}
                )
                conn.commit() # Explicit commit for this update
                return None, f"Usuário bloqueado por {BLOQUEIO_MINUTOS} minutos"
            else:
                conn.execute(
                    text("UPDATE usuarios SET tentativas_invalidas=:tentativas WHERE id=:id"),
                    {"tentativas": tentativas, "id": user_id}
                )
                conn.commit() # Explicit commit for this update
                return (
                    None,
                    f"Senha incorreta. Tentativas restantes: {MAX_TENTATIVAS - tentativas}",
                )
        # Sucesso
        conn.execute(
            text("UPDATE usuarios SET tentativas_invalidas=0, bloqueado_ate=NULL, ultimo_login=:now WHERE id=:id"),
            {"now": now, "id": user_id}
        )
        conn.commit() # Explicit commit for this update
        return role, None


# --- Solicitar redefinição de senha ---
def solicitar_redefinicao(username):
    with get_db_connection() as conn:
        conn.execute(
            text("UPDATE usuarios SET redefinir_solicitado=1 WHERE username=:username"),
            {"username": username}
        )
        conn.commit()


# --- Aprovar redefinição de senha (admin) ---
def aprovar_redefinicao(username):
    with get_db_connection() as conn:
        conn.execute(
            text("UPDATE usuarios SET redefinir_aprovado=1 WHERE username=:username"),
            {"username": username}
        )
        conn.commit()


# --- Redefinir senha (após aprovação) ---
def redefinir_senha(username, nova_senha):
    with get_db_connection() as conn:
        result = conn.execute(text("SELECT redefinir_aprovado FROM usuarios WHERE username=:username"), {"username": username}).fetchone()
        if not result or not result[0]:
            raise ValueError("Redefinição não aprovada")
        password_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()
        conn.execute(
            text("UPDATE usuarios SET password_hash=:password_hash, redefinir_solicitado=0, redefinir_aprovado=0 WHERE username=:username"),
            {"password_hash": password_hash, "username": username},
        )
        conn.commit()


# --- Expiração de sessão ---
def sessao_expirada(ultimo_login):
    if not ultimo_login:
        return True
    try:
        # ultimo_login já deve ser um objeto datetime do pyodbc
        return (datetime.now() - ultimo_login) > timedelta(minutes=SESSAO_MINUTOS)
    except Exception:
        return True
