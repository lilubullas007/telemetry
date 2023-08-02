start:
	minikube start --nodes 2 -p multinode-demo --force

stop:
	minikube stop -p multinode-demo

run:
	kubectl apply -f "kubernetes-prometheus/*.yaml"
	kubectl apply -f "kubernetes-node-exporter/*.yaml"
	kubectl apply -f "kube-state-metrics-configs/*.yaml"
	kubectl apply -f "kubernetes-grafana/*.yaml"
	kubectl apply -f "otel-collector/*.yaml"

delete:
	kubectl delete -f "kubernetes-prometheus/*.yaml"
	kubectl delete -f "kubernetes-node-exporter/*.yaml"
	kubectl delete -f "kube-state-metrics-configs/*.yaml"
	kubectl delete -f "kubernetes-grafana/*.yaml"
	kubectl delete -f "otel-collector/*.yaml"