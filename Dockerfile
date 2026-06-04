FROM python:3.10-slim

WORKDIR /app

# Instala certificados para o bot conseguir se conectar à internet sem bloqueios de SSL
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Comando que inicia a aplicação
CMD ["python", "app.py"]
