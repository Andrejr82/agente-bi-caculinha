# Use uma imagem base oficial do Python
# Escolha uma versão que seja compatível com suas dependências e que seja leve (slim-buster)
FROM python:3.11-slim-buster

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo requirements.txt para o diretório de trabalho
# e instala as dependências. Fazemos isso em uma etapa separada
# para aproveitar o cache do Docker (se requirements.txt não mudar,
# esta etapa não será reexecutada).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação para o diretório de trabalho
COPY . .

# Expõe a porta que o Streamlit usa (padrão é 8501)
EXPOSE 8501

# Define a variável de ambiente para o Streamlit não abrir o navegador automaticamente
ENV STREAMLIT_SERVER_HEADLESS=true

# Comando para iniciar a aplicação Streamlit
# Certifique-se de que o nome do arquivo principal do Streamlit está correto
CMD streamlit run streamlit_app.py
