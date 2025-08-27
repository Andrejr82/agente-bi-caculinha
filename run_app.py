# run_app.py
import subprocess
import sys
import time
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_command(command, name):
    """Executa um comando em um subprocesso e retorna o processo."""
    logging.info(f"Iniciando o processo '{name}': {' '.join(command)}")
    try:
        # Usar sys.executable garante que estamos usando o interpretador python do ambiente atual
        process = subprocess.Popen(command, text=True)
        time.sleep(5) # Dá um tempo para o processo iniciar e possivelmente falhar
        
        # Verifica se o processo terminou com erro logo no início
        if process.poll() is not None and process.returncode != 0:
            logging.error(f"Falha ao iniciar o processo '{name}'.")
            return None
        
        logging.info(f"Processo '{name}' iniciado com sucesso com PID: {process.pid}")
        return process
    except FileNotFoundError:
        logging.error(f"Comando não encontrado para o processo '{name}'. Certifique-se de que o executável está no PATH.")
        return None
    except Exception as e:
        logging.error(f"Um erro inesperado ocorreu ao iniciar o processo '{name}': {e}")
        return None

def main():
    """Função principal para iniciar todos os serviços da aplicação."""
    logging.info("Iniciando o orquestrador da aplicação Agent_BI...")

    # Comando para iniciar o backend FastAPI com uvicorn
    backend_command = [sys.executable, "-m", "uvicorn", "core.main:app"]
    
    # Comando para iniciar o frontend com Streamlit
    frontend_command = [sys.executable, "-m", "streamlit", "run", "streamlit_app.py"]

    # Inicia os processos
    backend_process = run_command(backend_command, "Backend FastAPI")
    frontend_process = run_command(frontend_command, "Frontend Streamlit")

    if not backend_process or not frontend_process:
        logging.error("Um ou mais processos falharam ao iniciar. Encerrando o orquestrador.")
        sys.exit(1)

    logging.info("Aplicação iniciada. Pressione Ctrl+C para encerrar todos os processos.")

    try:
        # Mantém o script principal rodando para monitorar os subprocessos
        while True:
            if backend_process.poll() is not None:
                logging.warning("O processo de backend foi encerrado inesperadamente.")
                break
            if frontend_process.poll() is not None:
                logging.warning("O processo de frontend foi encerrado inesperadamente.")
                break
            time.sleep(2)
    except KeyboardInterrupt:
        logging.info("Recebido sinal de interrupção (Ctrl+C). Encerrando processos...")
    finally:
        if backend_process.poll() is None:
            backend_process.terminate()
            logging.info("Processo de backend encerrado.")
        if frontend_process.poll() is None:
            frontend_process.terminate()
            logging.info("Processo de frontend encerrado.")
        logging.info("Orquestrador finalizado.")

if __name__ == "__main__":
    main()