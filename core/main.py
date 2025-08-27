# core/main.py
import uvicorn
import logging
import subprocess
import sys
import os
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Configuração do logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Lógica para ler credenciais ---
def get_db_credentials_from_file() -> dict:
    """Lê as credenciais do banco de dados do arquivo conexao.txt."""
    creds = {}
    try:
        # O caminho é relativo à raiz do projeto, assumindo que o backend é executado de lá
        with open("conexao.txt", "r") as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    creds[key.strip().lower()] = value.strip().strip("'\"")
    except FileNotFoundError:
        logging.warning("Arquivo conexao.txt não encontrado. O pipeline agendado pode falhar se não houver variáveis de ambiente.")
    except Exception as e:
        logging.error(f"Erro ao ler conexao.txt: {e}")
    return creds

# --- Lógica do Pipeline ---
def trigger_pipeline_subprocess():
    """Aciona a execução do script do pipeline de dados como um subprocesso."""
    logging.info("Acionando a execução do pipeline de dados via subprocesso...")
    
    creds = get_db_credentials_from_file()
    if not all(k in creds for k in ['server', 'database', 'user', 'password']):
        logging.error("Credenciais insuficientes no conexao.txt para executar o pipeline.")
        return

    command = [
        sys.executable, 
        "scripts/data_pipeline.py",
        "--server", creds['server'],
        "--database", creds['database'],
        "--user", creds['user'],
        "--password", creds['password']
    ]

    try:
        # Executa o script e espera completar, capturando a saída
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        logging.info("Subprocesso do pipeline executado com sucesso.")
        logging.info(f"STDOUT:\n{process.stdout}")
        if process.stderr:
            logging.warning(f"STDERR:\n{process.stderr}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Subprocesso do pipeline falhou com código de saída {e.returncode}")
        logging.error(f"STDERR:\n{e.stderr}")
    except Exception as e:
        logging.error(f"Falha ao executar o subprocesso do pipeline: {e}", exc_info=True)

# --- Configuração da API e Agendador ---
app = FastAPI(
    title="Agent_BI Backend",
    description="Serviço de backend para o Agente de BI, incluindo agendamento de tarefas.",
    version="1.1.0"
)
scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup_event():
    logging.info("Iniciando o agendador de tarefas do backend...")
    scheduler.add_job(
        trigger_pipeline_subprocess,
        trigger=CronTrigger(hour='8,20', minute='0', second='0'),
        id="data_pipeline_job",
        name="Pipeline de Extração de Dados SQL para Parquet",
        replace_existing=True
    )
    scheduler.start()
    logging.info("Agendador iniciado. Pipeline de dados agendado para 08:00 e 20:00.")

@app.on_event("shutdown")
async def shutdown_event():
    logging.info("Encerrando o agendador de tarefas...")
    scheduler.shutdown()

@app.get("/status", tags=["Monitoring"])
def read_root():
    return {"status": "Serviço de Backend do Agent_BI está no ar."}

@app.post("/run-pipeline", tags=["Actions"])
async def trigger_pipeline_endpoint():
    logging.info("Execução manual do pipeline de dados acionada via API.")
    scheduler.add_job(trigger_pipeline_subprocess, 'date', name="Execução Manual do Pipeline")
    return {"message": "Execução do pipeline de dados iniciada."}

# Para executar este servidor diretamente:
# uvicorn core.main:app --reload