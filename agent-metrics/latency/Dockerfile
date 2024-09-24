# Usa una imagen base de Python
FROM python:3.11-slim

# Instala iputils-ping para permitir el uso de ping
RUN apt-get update && apt-get install -y iputils-ping && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de tu aplicación al contenedor
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de tu código
COPY . .

# Establece las variables de entorno
ENV SOURCE_IP="10.208.99.108"
ENV COLLECTOR_ENDPOINT="http://10.208.99.108:30807"
ENV CLUSTER="IBM"
ENV INTERVAL_MS="30000"

# Expon el puerto en el que la aplicación se ejecutará
EXPOSE 8000


# Comando para ejecutar la aplicación
CMD ["uvicorn", "metric_latency:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
