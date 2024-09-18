import random
import time
from opentelemetry import metrics
from opentelemetry.metrics import Observation, CallbackOptions
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_NAMESPACE, SERVICE_VERSION, Resource


# Callback to provide the current temperature
def get_current_temperature(_: CallbackOptions):
   temperature_rackA = 24.5
   temperature_rackB = 26.0
   attributesA = {"rack_id": "rackA"}
   attributesB = {"rack_id": "rackB"}
   yield Observation (temperature_rackB, attributesB) # Simulate getting the current temperature

# Callback to provide the current energy consumption
def get_current_energy_consumption(_: CallbackOptions):
    energy_rackA = 1000
    energy_rackB = 2500
    attributesA = {"rack_id": "rackA"}
    attributesB = {"rack_id": "rackB"}
    yield Observation (energy_rackA, attributesA) # Simulate getting the current energy consumption


# Service name is required for most backends
resource = Resource(attributes={
    SERVICE_NAME: "dice-roller",
    SERVICE_NAMESPACE: "devx",
    SERVICE_VERSION: "1.0.0"
})

COLLECTOR_ENDPOINT = "http://10.208.99.108:30807"
INTERVAL_SEC = 10

# Boiler plate initialization
metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=COLLECTOR_ENDPOINT, insecure=True), INTERVAL_SEC)
provider = MeterProvider(metric_readers=[metric_reader], resource=resource)

# Sets the global default meter provider
metrics.set_meter_provider(provider)

# Creates a meter from the global meter provider
meter = metrics.get_meter("dice-roller", "1.0.0")


# Create instruments
temperature_gauge = meter.create_observable_gauge(
    name="cluster.temperature",
    description="Temperature of the cluster in Celsius",
    unit="C",
    callbacks=[get_current_temperature],
)

energy_gauge = meter.create_observable_gauge(
    name="cluster.energy_consumption",
    description="Energy consumption of the cluster in kWh",
    unit="kWh",
    callbacks=[get_current_energy_consumption],
)


print("Sending metrics...")
