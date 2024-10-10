from prometheus_api_client import PrometheusConnect
prom = PrometheusConnect(url ="http://192.168.49.2:30000", disable_ssl=True)

print(prom.custom_query(query="sum (rate (container_cpu_usage_seconds_total[2m])) / avg (machine_cpu_cores) * 100"))