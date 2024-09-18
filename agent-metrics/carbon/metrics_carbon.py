from fastapi import FastAPI, HTTPException, Request
from typing import List, Dict
from opentelemetry import metrics
from opentelemetry.metrics import Observation, CallbackOptions
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_NAMESPACE, SERVICE_VERSION, Resource
from dotenv import load_dotenv
from datetime import datetime
import time
import os
import requests
import logging
import threading


load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Initialize logger
logging.basicConfig(level=logging.DEBUG)

LATITUDE = os.getenv("LATITUDE")
LONGITUDE = os.getenv("LONGITUDE")
API_KEY = os.getenv("API_KEY")
COLLECTOR_ENDPOINT = os.getenv("COLLECTOR_ENDPOINT")
INTERVAL_MS = os.getenv("INTERVAL_MS")

# In-memory list to store latitudes and longitudes
lat_lon_list = []

# Configure OpenTelemetry
resource = Resource(attributes={
    SERVICE_NAME: "cluster-monitor",
    SERVICE_NAMESPACE: "fluidos",
    SERVICE_VERSION: "1.0.0"
})

metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=COLLECTOR_ENDPOINT, insecure=True), int(INTERVAL_MS))
provider = MeterProvider(metric_readers=[metric_reader], resource=resource)
metrics.set_meter_provider(provider)
meter = metrics.get_meter("cluster-monitor", "1.0.0")

def get_live_carbon_intensity(lat: str, lon: str):
    BASE_URL = 'https://api.electricitymap.org/v3'
    HEADERS = {'auth-token': str(API_KEY)}
    url = f"{BASE_URL}/carbon-intensity/latest"
    params = {'lat': lat, 'lon': lon}

    logging.debug(f"Request URL: {url}")
    logging.debug(f"Request params: {params}")

    response = requests.get(url, headers=HEADERS, params=params)

    logging.debug(f"Response status code: {response.status_code}")
    logging.debug(f"Response content: {response.content}")

    if response.status_code == 200:
        return response.json()["carbonIntensity"]
    else:
        return None

def get_forecasted_carbon_intensity(lat: str, lon: str):
    BASE_URL = 'https://api.electricitymap.org/v3'
    HEADERS = {'auth-token': str(API_KEY)}
    url = f"{BASE_URL}/carbon-intensity/forecast"
    params = {'lat': lat, 'lon': lon}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        forecast_values = []
        for forecast_item in response.json()["forecast"]:
            forecast_values.append(forecast_item['carbonIntensity'])
        return forecast_values
    else:
        logging.exception(f"Error fetching forecasted data: {response.status_code}")
        logging.exception(f"Error: {response.reason}")
        return None

def get_live_carbon(_: CallbackOptions):
    for loc in lat_lon_list:
        lat, lon = loc['lat'], loc['lon']
        carbon = get_live_carbon_intensity(lat, lon)
        attributes = {'latitude': lat, 'longitude': lon}
        if carbon is not None:
            yield Observation(carbon, attributes)

def get_forecast_carbon(_: CallbackOptions):
    for loc in lat_lon_list:
        lat, lon = loc['lat'], loc['lon']
        carbon = get_forecasted_carbon_intensity(lat, lon)
        date = datetime.now()
        formatted_date = date.strftime("%m/%d/%Y-%H:%M")
        if carbon is not None:
            for idx, forecast_item in enumerate(carbon):
                attributes = {'latitude': lat, 'longitude': lon, 'date': formatted_date}
                attributes['forecast'] = idx
                yield Observation(carbon[idx], attributes)



meter.create_observable_gauge(
    name=f"node.fluidos.carbon",
    description="Current carbon intensity",
    unit="gCO2/kWh",
    callbacks=[get_live_carbon],
)

meter.create_observable_gauge(
    name=f"node.fluidos.carbon_forecast",
    description="Forecasted carbon intensity",
    unit="gCO2/kWh",
    callbacks=[get_forecast_carbon],
)

@app.post('/cluster/')
def add_cluster(new_location: Dict):
    print(new_location)
    try:
        lat = new_location['lat']
        lon = new_location['lon']
    except:
        raise HTTPException(status_code=400, detail="Bad Format")
    if lat and lon:
        lat_lon_list.append({'lat': lat, 'lon': lon})
        logging.info(f"Added cluster: lat={lat}, lon={lon}")
        thread = threading.Thread(target=metric_reader.force_flush)
        thread.start()
        return {"status": "success", "lat": lat, "lon": lon}
    else:
        raise HTTPException(status_code=400, detail="Error adding")

@app.get('/clusters/')
def list_clusters():
    return lat_lon_list

@app.delete('/cluster/')
def delete_cluster(new_location: Dict):
    try:
        lat = new_location['lat']
        lon = new_location['lon']
    except:
        raise HTTPException(status_code=400, detail="Bad Format")
    lat_lon_list_aux = [loc for loc in lat_lon_list if not (loc['lat'] == lat and loc['lon'] == lon)]
    if len(lat_lon_list) == len(lat_lon_list_aux):
        raise HTTPException(status_code=400, detail="Not deleted, no exists")
    return {"message": (f"Deleted cluster: lat={lat}, lon={lon}")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
