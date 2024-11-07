from flask import Flask, jsonify
import os
import signal
import psutil

app = Flask(__name__)

@app.route('/reload', methods=['POST'])
def reload_config():
    # Buscar el proceso de OpenTelemetry Collector por su nombre
    process_name = "otelcol-contrib"
    for proc in psutil.process_iter(['pid', 'name']):
        if process_name in proc.info['name']:
            pid = proc.info['pid']
            print(pid)
            os.system('sudo kill -SIGHUP {}'.format(pid))  # Envía SIGHUP al proceso encontrado
            return jsonify({"message": "SIGHUP sent to OpenTelemetry Collector", "pid": pid}), 200
    return jsonify({"error": "Process not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
