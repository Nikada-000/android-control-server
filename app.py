from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory device store (for demo)
devices = []

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    device_id = data.get("device_id")
    
    # Check if device already exists
    existing = next((d for d in devices if d["device_id"] == device_id), None)
    if not existing:
        data["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        devices.append(data)
    else:
        existing.update(data)
        existing["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"📲 Device registered: {data}")
    return jsonify({"message": "Device registered"}), 200

@app.route("/devices", methods=["GET"])
def get_devices():
    return jsonify(devices), 200

# Optional home page
@app.route("/", methods=["GET"])
def home():
    return "✅ Android Control Server is running."

@app.route("/command", methods=["POST"])
def send_command():
    data = request.json
    device_id = data.get("device_id")
    command = data.get("command")

    # Find the device
    device = next((d for d in devices if d["device_id"] == device_id), None)
    if not device:
        return jsonify({"error": "Device not found"}), 404

    # Just logging for now, real implementation needed
    print(f"📤 Command '{command}' sent to {device_id}")
    return jsonify({"message": f"Command '{command}' sent to {device_id}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
