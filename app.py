# app.py
from flask import Flask, request, jsonify
import time

app = Flask(__name__)
devices = {}  # Store devices in memory

@app.route("/")
def home():
    return "✅ Android Control Server Running"

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    device_id = data.get("device_id")
    if not device_id:
        return jsonify({"error": "Missing device_id"}), 400

    devices[device_id] = {
        "device_id": device_id,
        "name": data.get("name", "Unknown Device"),
        "ip": data.get("ip", request.remote_addr),
        "status": data.get("status", "online"),
        "last_seen": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    return jsonify({"message": "Device registered successfully"}), 200

@app.route("/devices", methods=["GET"])
def get_devices():
    return jsonify(list(devices.values()))

@app.route("/command", methods=["POST"])
def send_command():
    data = request.json
    device_id = data.get("device_id")
    command = data.get("command")
    return jsonify({"message": f"Command '{command}' sent to {device_id}"})
