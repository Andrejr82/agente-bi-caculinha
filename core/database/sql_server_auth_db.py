import pyodbc
import os
from dotenv import load_dotenv
import bcrypt
from datetime import datetime, timedelta

load_dotenv()

# --- Configurações do Banco de Dados ---
MSSQL_SERVER = os.getenv("MSSQL_SERVER")
MSSQL_DATABASE = os.getenv("MSSQL_DATABASE")
MSSQL_USER = os.getenv("MSSQL_USER")
MSSQL_PASSWORD = os.getenv("MSSQL_PASSWORD")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
MSSQL_TRUST_SERVER_CERTIFICATE = os.getenv("MSSQL_TRUST_SERVER_CERTIFICATE", "yes")
MSSQL_ENCRYPT = os.getenv("MSSQL_ENCRYPT", "no")

# --- Constantes de Autenticação ---
MAX_TENTATIVAS = 5
BLOQUEIO_MINUTOS = 15
SESSAO_MINUTOS = 30


def get_db_connection():
    conn_str = (
        f"DRIVER={{{DB_DRIVER}}};"
        f"SERVER={MSSQL_SERVER};"
        f"DATABASE={MSSQL_DATABASE};"
        f"UID={MSSQL_USER};"
        f"PWD={MSSQL_PASSWORD};"
        f"Encrypt={MSSQL_ENCRYPT};"
        f"TrustServerCertificate={MSSQL_TRUST_SERVER_CERTIFICATE};"
    )
    return pyodbc.connect(conn_str)


# --- Inicialização do banco (Cria a tabela se não existir) ---
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
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
    conn.commit()
    conn.close()


# --- Criação de usuário ---
def criar_usuario(username, password, role="user"):
    conn = get_db_connection()
    cursor = conn.cursor()
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role),
        )
        conn.commit()
    except pyodbc.IntegrityError:
        raise ValueError("Usuário já existe")
    finally:
        conn.close()


# --- Autenticação ---
def autenticar_usuario(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, password_hash, ativo, tentativas_invalidas, bloqueado_ate, role FROM usuarios WHERE username=?",
        (username,),
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None, "Usuário não encontrado"
    user_id, password_hash, ativo, tentativas, bloqueado_ate, role = row
    now = datetime.now()

    if not ativo:
        conn.close()
        return None, "Usuário inativo ou bloqueado"

    if bloqueado_ate:
        if now < bloqueado_ate:
            conn.close()
            return None, f"Usuário bloqueado até {bloqueado_ate.strftime('%Y-%m-%d %H:%M:%S')}"

    if not bcrypt.checkpw(password.encode(), password_hash.encode()):
        tentativas += 1
        if tentativas >= MAX_TENTATIVAS:
            bloqueado_ate = now + timedelta(minutes=BLOQUEIO_MINUTOS)
            cursor.execute(
                "UPDATE usuarios SET tentativas_invalidas=?, bloqueado_ate=? WHERE id=?",
                (tentativas, bloqueado_ate, user_id),
            )
            conn.commit()
            conn.close()
            return None, f"Usuário bloqueado por {BLOQUEIO_MINUTOS} minutos"
        else:
            cursor.execute(
                "UPDATE usuarios SET tentativas_invalidas=? WHERE id=?",
                (tentativas, user_id),
            )
            conn.commit()
            conn.close()
            return (
                None,
                f"Senha incorreta. Tentativas restantes: {MAX_TENTATIVAS - tentativas}",
            )
    # Sucesso
    cursor.execute(
        "UPDATE usuarios SET tentativas_invalidas=0, bloqueado_ate=NULL, ultimo_login=? WHERE id=?",
        (now, user_id),
    )
    conn.commit()
    conn.close()
    return role, None


# --- Solicitar redefinição de senha ---
def solicitar_redefinicao(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET redefinir_solicitado=1 WHERE username=?", (username,)
    )
    conn.commit()
    conn.close()


# --- Aprovar redefinição de senha (admin) ---
def aprovar_redefinicao(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET redefinir_aprovado=1 WHERE username=?", (username,))
    conn.commit()
    conn.close()


# --- Redefinir senha (após aprovação) ---
def redefinir_senha(username, nova_senha):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT redefinir_aprovado FROM usuarios WHERE username=?", (username,))
    row = cursor.fetchone()
    if not row or not row[0]:
        conn.close()
        raise ValueError("Redefinição não aprovada")
    password_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()
    cursor.execute(
        "UPDATE usuarios SET password_hash=?, redefinir_solicitado=0, redefinir_aprovado=0 WHERE username=?",
        (password_hash, username),
    )
    conn.commit()
    conn.close()


# --- Expiração de sessão ---
def sessao_expirada(ultimo_login):
    if not ultimo_login:
        return True
    try:
        # ultimo_login já deve ser um objeto datetime do pyodbc
        return (datetime.now() - ultimo_login) > timedelta(minutes=SESSAO_MINUTOS)
    except Exception:
        return True
