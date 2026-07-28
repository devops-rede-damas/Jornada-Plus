# Imagem base enxuta com Python
FROM python:3.12-slim

# Evita arquivos .pyc e garante logs sem buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências primeiro (melhor cache de build)
# cryptography é necessário para autenticação caching_sha2_password do MySQL 8
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn cryptography

# Copia o restante da aplicação
COPY . .

# Porta do frontend Flask
EXPOSE 5001

# Sobe a aplicação com Gunicorn (fábrica criar_app)
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "3", "app:criar_app()"]
