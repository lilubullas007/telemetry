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
ENV LATITUDE="48.864716"
ENV LONGITUDE="2.349014"
ENV API_KEY=""
ENV COLLECTOR_ENDPOINT="http://10.208.99.108:30807"
ENV INTERVAL_MS="3600000"

# Expon el puerto en el que la aplicación se ejecutará
EXPOSE 8001

# Comando para ejecutar la aplicación
CMD ["uvicorn", "metrics_carbon:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
