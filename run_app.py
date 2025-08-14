import subprocess
import sys

def main():
    """Executa a aplicação Streamlit."""
    try:
        print("Iniciando a aplicação Streamlit...")
        subprocess.run(["streamlit", "run", "streamlit_app.py"], check=True)
    except FileNotFoundError:
        print("Erro: O comando 'streamlit' não foi encontrado.")
        print("Verifique se o Streamlit está instalado e no PATH do sistema.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Ocorreu um erro ao executar a aplicação: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
