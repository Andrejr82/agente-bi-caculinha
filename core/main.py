# import logging
import os
import sys

from core.agents.supervisor import initialize_agent_for_session
from core.utils.db_check import check_database_connection
from core.utils.db_structure_loader import carregar_estrutura_banco
from core.utils.env_setup import setup_environment

"""
Módulo principal para iniciar o agente Caçulinha BI.
Este arquivo serve como ponto de entrada centralizado para o projeto.
"""

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


try:
    pass
except ImportError as e:
    print(f"\n[ERRO DE IMPORTAÇÃO] {e}")
    print(
        "Isso pode indicar que algumas dependências não estão instaladas corretamente."
    )
    print(
        'Execute "python agent/core/check_dependencies.py" para verificar e instalar as dependências necessárias.'
    )
    sys.exit(1)


def validar_estrutura():
    estrutura = carregar_estrutura_banco()
    if estrutura is None:
        print(
            "[ERRO] Estrutura do banco não encontrada ou inválida "
            "(estrutura_completa_banco.json)."
        )
        return False
    return True


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    setup_environment(base_dir)

    if not check_database_connection():
        print(
            "[ERRO] Falha na conexão com o banco de dados. "
            "Corrija as configurações e tente novamente."
        )
        sys.exit(1)

    if not validar_estrutura():
        sys.exit(1)

    try:
        # Inicializa o supervisor (ou agente principal)
        initialize_agent_for_session()
        print("Supervisor/Agente inicializado com sucesso.")
        # Aqui você pode adicionar lógica para rodar um servidor Flask/FastAPI se necessário
        # Variável 'supervisor' não utilizada explicitamente (ok para inicialização)
    except KeyboardInterrupt:
        print("\nCaçulinha: Sessão interrompida. Até logo!")
    except Exception as e:
        print(f"\n[ERRO INESPERADO] Ocorreu um erro: {e}")
        print("Por favor, tente novamente ou reinicie o agente.")


if __name__ == "__main__":
    main()
