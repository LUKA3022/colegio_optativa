FROM python:3.12-slim

# Instalar dependencias del sistema operativo
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar el gestor de paquetes uv
RUN pip install uv

WORKDIR /app

# Copiar archivos de dependencias
COPY pyproject.toml uv.lock ./

# Instalar las dependencias del proyecto
RUN uv sync --frozen

# Copiar el código fuente
COPY . .

EXPOSE 5000

# [Inferencia] Se asume que el archivo principal de tu aplicación se llama app.py
CMD ["uv", "run", "flask", "--app", "app.py", "run", "--host=0.0.0.0"]
