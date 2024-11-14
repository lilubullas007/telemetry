from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yaml
from kubernetes import client, config

# FastAPI
app = FastAPI()

# Request data-model
class PipelineRequest(BaseModel):
    prometheusExporter: str
    domainID: str
    flavorID: str

# Method to load Kubernetes config
def load_kubernetes_config():
    try:
        config.load_incluster_config()
    except:
        config.load_kube_config()

# Update ConfigMap method
def update_configmap(namespace: str, configmap_name: str, new_data: dict):
    # Connect with k8s cluster
    load_kubernetes_config()
    v1 = client.CoreV1Api()

    # Get current ConfigMap
    configmap = v1.read_namespaced_config_map(configmap_name, namespace)
    configmap_yaml = yaml.safe_load(configmap.data['collector.yaml'])

    print(configmap_yaml)

    # Update processors, exporters and pipelines
    domainID = new_data["domainID"]
    flavorID = new_data["flavorID"]
    exporter = new_data["prometheusExporter"]

    # Filter
    filter_name = f"filter/basicmetrics{domainID}{flavorID}"
    configmap_yaml["processors"][filter_name] = {
        "error_mode": "ignore",
        "metrics": {
            "metric": [
                f'resource.attributes["k8s.node.name"] != "{flavorID}"'
            ]
        }
    }

    # Exporter
    exporter_name = f"prometheusremotewrite/{domainID}"
    configmap_yaml["exporters"][exporter_name] = {
        "endpoint": exporter
    }

    # Pipeline
    pipeline_name = f"metrics/{domainID}{flavorID}"
    configmap_yaml["service"]["pipelines"][pipeline_name] = {
        "receivers": ["kubeletstats", "prometheus", "otlp", "k8s_cluster", "hostmetrics"],
        "processors": [filter_name, "attributes/metrics", "k8sattributes", "resource", "batch"],
        "exporters": [exporter_name]
    }

    # Aux functionality: insert new action (check whether ConfigMap is up to date)
    configmap_yaml["processors"]["attributes/metrics"]["actions"].append({
        "action": "insert",
        "key": "source",
        "value": "opentelemetry"
    })

    # Convert to YAML
    updated_yaml = yaml.safe_dump(configmap_yaml)

    print(updated_yaml)

    # Update opentelemetrycollector ConfigMap
    configmap.data['collector.yaml'] = updated_yaml
    v1.replace_namespaced_config_map(configmap_name, namespace, configmap)

# Endpoint to create new pipelines
@app.post("/addpipeline/transfermetrics")
def add_pipeline(request: PipelineRequest):
    try:
        # Basic parameters
        namespace = "monitoring"
        configmap_name = "collector-config"

        # Update ConfigMap
        update_configmap(namespace, configmap_name, request.dict())

        return {"message": "Pipeline created and ConfigMap successfully updated.\n"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))