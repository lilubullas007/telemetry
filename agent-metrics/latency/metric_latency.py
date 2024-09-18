from fastapi import FastAPI, HTTPException, Request
from typing import List, Dict
from opentelemetry import metrics
from opentelemetry.metrics import Observation, CallbackOptions
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_NAMESPACE, SERVICE_VERSION, Resource
import time
import os
import subprocess
import threading
from dotenv import load_dotenv

load_dotenv()


# Initialize FastAPI app
app = FastAPI()

# List to store IPs to be pinged
#ip_list = []
ip_list = ["10.208.99.106"]
#cluster_list = [{"domain": "UMU", "cluster": "UMU", "node_ip": "10.208.99.106"}]
cluster_list = []
SOURCE_IP = os.getenv("SOURCE_IP", "Unknown")
CLUSTER = os.getenv("CLUSTER", "Unknown")
COLLECTOR_ENDPOINT = os.getenv("COLLECTOR_ENDPOINT")
INTERVAL_MS = os.getenv("INTERVAL_MS")

# Function to perform a ping and return the average latency
def ping_node(node_ip):
    try:
        print(f"Ping to {node_ip}.")
        # Run the ping command
        result = subprocess.run(["ping", "-c", "4", node_ip], capture_output=True, text=True)
        # Parse the output for average latency
        if result.returncode == 0:
            output = result.stdout
            # Extract the average latency value from the ping output
            avg_latency = float(output.split("/")[-3])  # Parse the avg time from the output
            return avg_latency
        else:
            print(f"Ping to {node_ip} failed.")
            return None
    except Exception as e:
        print(f"Error pinging {node_ip}: {e}")
        return None

# Callback to provide the current latency between nodes
def get_current_latency(_: CallbackOptions):
    for cluster_remote in cluster_list:
        latency = ping_node(cluster_remote["node_ip"])
        attributes = {"from_node": CLUSTER, "to_cluster": cluster_remote["cluster"], "from_node": SOURCE_IP, "to_node": cluster_remote["node_ip"]}
        if latency is not None:
            yield Observation(latency, attributes)

# OpenTelemetry resource definition
resource = Resource(attributes={
    SERVICE_NAME: "cluster-monitor",
    SERVICE_NAMESPACE: "fluidos",
    SERVICE_VERSION: "1.0.0"
})



# Initialization for OpenTelemetry Metric Exporting
metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=COLLECTOR_ENDPOINT, insecure=True), int(INTERVAL_MS))
provider = MeterProvider(metric_readers=[metric_reader], resource=resource)
metrics.set_meter_provider(provider)
meter = metrics.get_meter("cluster-monitor", "1.0.0")

# Create an observable gauge for latency
latency_gauge = meter.create_observable_gauge(
    name="node.fluidos.latency",
    description="Network latency between cluster nodes in milliseconds",
    unit="ms",
    callbacks=[get_current_latency],
)



@app.post("/cluster/")
def add_cluster(new_cluster: Dict):
    for cluster_remote in cluster_list:
        print(new_cluster)
        if new_cluster['node_ip'] == cluster_remote['node_ip']:
            raise HTTPException(status_code=400, detail="IP already exists in the list.")
    cluster_list.append(new_cluster)
    thread = threading.Thread(target=metric_reader.force_flush)
    thread.start()
    return {"message": f"IP {new_cluster['node_ip']} added to the ping list."}

@app.get("/clusters/")
def list_ips():
    return cluster_list

@app.delete("/cluster/")
def remove_ip(ip: str):
    for cluster_remote in cluster_list:
        if cluster_remote['node_ip'] == ip:
            cluster_list.remove(cluster_remote)
        return {"message": f"IP {ip} removed from the ping list."}
    else:
        raise HTTPException(status_code=404, detail="IP not found in the list.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)