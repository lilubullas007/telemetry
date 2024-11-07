# Usa la imagen base de bitnami/kubectl
FROM bitnami/kubectl:latest

# Cambia temporalmente al usuario root para instalar curl
USER root

# Crear el directorio faltante, actualizar repositorios e instalar curl
RUN mkdir -p /var/lib/apt/lists/partial && \
    apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Regresa al usuario original sin privilegios
USER 1001