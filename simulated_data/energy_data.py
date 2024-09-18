import random
import time
import socket
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.metrics import Observation, CallbackOptions

# Function to get the IP address of the current machine
def get_instance_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

# Define the OTEL Collector endpoint using gRPC
COLLECTOR_ENDPOINT = "http://10.208.99.108:30807"
EXPORT_INTERVAL_SEC = 10  # Export interval in seconds

# Get the IP address of the instance
INSTANCE_IP = get_instance_ip()

# Set up the OpenTelemetry MeterProvider with a gRPC exporter
resource = Resource.create({
    "service.name": "battery-monitoring-service",
    "service.namespace": "example",
    "service.version": "1.0.0"
})

# Create the OTLP Metric Exporter using gRPC protocol
metric_exporter = OTLPMetricExporter(endpoint=COLLECTOR_ENDPOINT, insecure=True)

# Create a Periodic Exporting Metric Reader to export metrics at a defined interval
metric_reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=EXPORT_INTERVAL_SEC * 1000)

# Initialize the MeterProvider with the metric reader and resource
provider = MeterProvider(metric_readers=[metric_reader], resource=resource)

# Set the global meter provider
metrics.set_meter_provider(provider)

# Get a meter from the global meter provider
meter = metrics.get_meter("battery_monitor", "1.0.0")

# Function to generate random battery metrics
def get_battery_metrics(_: CallbackOptions):
    # Add 'instance' label with the IP address
    attributes = {"device": "battery0", "instance": INSTANCE_IP}
    
    # Generate random values for each metric within a reasonable range
    battery_metrics = [
        {"name": "battery_percentage", "description": "Current battery level as a percentage.", "unit": "%", "value": random.uniform(0, 100)},
        {"name": "battery_power_draw_watts", "description": "Current power draw of the battery in watts.", "unit": "W", "value": random.uniform(10, 30)},
        {"name": "battery_charge_rate_watts", "description": "Rate at which the battery is charging in watts.", "unit": "W", "value": random.uniform(15, 25)},
        {"name": "battery_discharge_rate_watts", "description": "Rate at which the battery is discharging in watts.", "unit": "W", "value": random.uniform(5, 15)},
        {"name": "battery_health_percent", "description": "Current health of the battery as a percentage.", "unit": "%", "value": random.uniform(80, 100)},
        {"name": "battery_voltage_volts", "description": "Current voltage of the battery in volts.", "unit": "V", "value": random.uniform(3.0, 4.2)},
        {"name": "battery_temperature_celsius", "description": "Current temperature of the battery in Celsius.", "unit": "C", "value": random.uniform(20, 40)},
        {"name": "battery_remaining_time_seconds", "description": "Estimated remaining time of battery usage in seconds.", "unit": "s", "value": random.uniform(3600, 14400)},  # 1 to 4 hours
        {"name": "battery_cycle_count", "description": "Total number of charge cycles the battery has undergone.", "unit": "count", "value": random.randint(100, 500)},
    ]

    # Yield each metric as an Observation
    for metric in battery_metrics:
        yield Observation(metric["value"], attributes)

# Create observable gauges for each battery metric
battery_percentage_gauge = meter.create_observable_gauge(
    name="battery_percentage",
    description="Current battery level as a percentage.",
    unit="%",
    callbacks=[get_battery_metrics],
)

battery_power_draw_watts_gauge = meter.create_observable_gauge(
    name="battery_power_draw_watts",
    description="Current power draw of the battery in watts.",
    unit="W",
    callbacks=[get_battery_metrics],
)

battery_charge_rate_watts_gauge = meter.create_observable_gauge(
    name="battery_charge_rate_watts",
    description="Rate at which the battery is charging in watts.",
    unit="W",
    callbacks=[get_battery_metrics],
)

battery_discharge_rate_watts_gauge = meter.create_observable_gauge(
    name="battery_discharge_rate_watts",
    description="Rate at which the battery is discharging in watts.",
    unit="W",
    callbacks=[get_battery_metrics],
)

battery_health_percent_gauge = meter.create_observable_gauge(
    name="battery_health_percent",
    description="Current health of the battery as a percentage.",
    unit="%",
    callbacks=[get_battery_metrics],
)

battery_voltage_volts_gauge = meter.create_observable_gauge(
    name="battery_voltage_volts",
    description="Current voltage of the battery in volts.",
    unit="V",
    callbacks=[get_battery_metrics],
)

battery_temperature_celsius_gauge = meter.create_observable_gauge(
    name="battery_temperature_celsius",
    description="Current temperature of the battery in Celsius.",
    unit="C",
    callbacks=[get_battery_metrics],
)

battery_remaining_time_seconds_gauge = meter.create_observable_gauge(
    name="battery_remaining_time_seconds",
    description="Estimated remaining time of battery usage in seconds.",
    unit="s",
    callbacks=[get_battery_metrics],
)

battery_cycle_count_gauge = meter.create_observable_gauge(
    name="battery_cycle_count",
    description="Total number of charge cycles the battery has undergone.",
    unit="count",
    callbacks=[get_battery_metrics],
)

print("Sending battery metrics using gRPC to OTEL Collector...")
while True:
    time.sleep(EXPORT_INTERVAL_SEC)  # Wait for the next export interval