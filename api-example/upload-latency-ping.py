from fastapi import FastAPI, HTTPException
from typing import List
import time
import subprocess
from opentelemetry import metrics
from opentelemetry.metrics import Observation, CallbackOptions
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_NAMESPACE, SERVICE_VERSION, Resource


# Initialize FastAPI app
app = FastAPI()

# List to store IPs to be pinged
#ip_list = []
ip_list = ["10.208.99.106"]
ip_src = "10.208.99.108"

# Function to perform a ping and return the average latency
def ping_node(node_ip):
    try:
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
    for ip in ip_list:
        latency = ping_node(ip)
        attributes = {"from_node": "IBM", "to_cluster": "UMU", "from_node": ip_src, "to_node": ip}
        yield Observation(latency, attributes)

    yield Observation(latency, attributes)  # Send latency from NodeB to NodeA

# OpenTelemetry resource definition
resource = Resource(attributes={
    SERVICE_NAME: "cluster-monitor",
    SERVICE_NAMESPACE: "devx",
    SERVICE_VERSION: "1.0.0"
})

COLLECTOR_ENDPOINT = "http://10.208.99.108:30807"  # Replace with your OTEL Collector endpoint
INTERVAL_SEC = 10

# Initialization for OpenTelemetry Metric Exporting
metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=COLLECTOR_ENDPOINT, insecure=True), INTERVAL_SEC)
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

print("Sending latency metrics...")

# Keep the script running
while True:
    time.sleep(30)
