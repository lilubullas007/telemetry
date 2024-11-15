from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

@app.route('/reload', methods=['POST'])
def reload_config():
    # Get OpenTelemetry pod name command
    get_pod_name_cmd = [
        "kubectl", "get", "pods", "-n", "monitoring", 
        "-l", "app.kubernetes.io/name=opentelemetrycollector", 
        "-o", "jsonpath={.items[0].metadata.name}"
    ]
    
    try:
        # Get pod name
        pod_name = subprocess.check_output(get_pod_name_cmd, text=True).strip()
        
        if not pod_name:
            return jsonify({"error": "OpenTelemetry pod not found"}), 404
        
        # Send SIGHUP signal to OpenTelemetry
        reload_cmd = [
            "kubectl", "debug", "-it", pod_name, "-n", "monitoring",
            "--image=busybox", "--target=opentelemetrycollector", 
            "--", "/bin/sh", "-c", "kill -HUP 1"
        ]
        
        subprocess.run(reload_cmd, check=True)
        
        return jsonify({"message": "SIGHUP sent to OpenTelemetry Collector", "pod": pod_name}), 200
    
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Failed to reload configuration", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
