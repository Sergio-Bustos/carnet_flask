FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

WORKDIR /app

# Dependencias del sistema + fuentes Liberation (equivalentes a Arial/Times)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libjpeg62-turbo \
    zlib1g \
    libopenblas0 \
    libgfortran5 \
    fonts-liberation \
    fonts-dejavu-core \
    fontconfig \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Crear directorios necesarios
RUN mkdir -p static/fotos static/qr static/carnets uploads \
    static/fotos_backup/por_fecha static/fotos_backup/metadatos \
    static/css static/js static/fonts templates instance

# Permisos
RUN chmod -R 777 static uploads instance templates

EXPOSE 5000

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000", "--reload"]