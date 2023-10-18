I have tested this demo in minikube, so the first step would be to install it (https://minikube.sigs.k8s.io/docs/start/) and launch it. Using ```make start``` should work.

# Starting the services
Using ```make run``` will start all the services:
- Prometheus
- Node Exporter
- kube-state-metrics
- Grafana
- OTEL Collector
- Alert Manager

We can check that every component is working with: ```kubectl get all -n monitoring```

## Opening the services
To be able to access each service you should execute: ```minikube -p multinode-demo service -n monitoring {SERVICE_NAME}```. E.g: ```minikube -p multinode-demo service -n monitoring grafana``` to make grafana accessible.

### Grafana
You can import dashboards in grafana. Once you log in as admin, with password admin, you can you to dashboards, New --> Import and select the grafana.json that is in kubernetes-grafana.

### Generating load
To check that the metrics and the dashboard update with changes, I've prepared a little test, in order to run it you should: ```make run-php``` and ```make run-load```. After waiting a couple of minutes you will see the changes.

### Asking prometheus for metrics
I have a python script, to run it you need to change the IP:PORT to the Prometheus service. ```python api/orchestrator.py```

### Prometheus rules
The rules are defined in kubernetes-prometheus/config-map.yaml in the prometheus-rules section. In order to connect the alerting with the alert manager you have to set the port in the alerting section in that same file.