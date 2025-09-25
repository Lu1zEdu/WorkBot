# Dockerfile
# Estágio 1: Builder - Instala as dependências de forma segura
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Estágio 2: Production - A imagem final, pequena e limpa
FROM python:3.11-slim
WORKDIR /app

# Copia apenas as dependências já instaladas do estágio anterior
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copia o código da aplicação
COPY . .

# Comando para executar o bot
CMD ["python", "bot.py"]