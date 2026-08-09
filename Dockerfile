FROM python:3.11-slim

# Evita que o Python grave arquivos .pyc no disco e força o log no terminal
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instala dependências do sistema para o PostGIS (GDAL, GEOS)
RUN apt-get update \
    && apt-get install -y binutils libproj-dev gdal-bin python3-gdal \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/