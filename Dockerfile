# Imagem base oficial do Python
FROM python:3.13-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala o Poetry
RUN pip install poetry

# Copia apenas os arquivos de dependências primeiro
# Isso aproveita o cache do Docker — se as dependências não mudaram,
# não precisa reinstalar tudo a cada build
COPY pyproject.toml poetry.lock* ./

# Instala as dependências sem criar ambiente virtual
# dentro do container o isolamento já é garantido pelo próprio container
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction

# Copia o restante do código
COPY . .

# Porta que a aplicação vai expor
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]