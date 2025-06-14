
from flask import Flask, request, jsonify
from datetime import datetime
import base64, os

app = Flask(__name__)

devices = {}
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    device_id = data.get("device_id")
    if not device_id:
        return jsonify({"error": "No device_id"}), 400
    data["last_seen"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    devices[device_id] = data
    return jsonify({"message": "Registered"}), 200

@app.route("/devices", methods=["GET"])
def list_devices():
    return jsonify(list(devices.values())), 200

@app.route("/command", methods=["POST"])
def send_command():
    data = request.get_json()
    device_id = data.get("device_id")
    command = data.get("command")
    if device_id in devices:
        devices[device_id]["pending_command"] = command
        return jsonify({"message": "Command sent"}), 200
    return jsonify({"error": "Device not found"}), 404

@app.route("/poll/<device_id>", methods=["GET"])
def poll(device_id):
    device = devices.get(device_id)
    if not device:
        return jsonify({"error": "Device not registered"}), 404
    command = device.pop("pending_command", None)
    return jsonify({"command": command}), 200

@app.route("/upload_photo", methods=["POST"])
def upload_photo():
    data = request.get_json()
    device_id = data.get("device_id")
    image_b64 = data.get("image")

    if not (device_id and image_b64):
        return jsonify({"error": "Missing data"}), 400

    filename = f"{device_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.jpg"
    path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        with open(path, "wb") as f:
            f.write(base64.b64decode(image_b64))
        return jsonify({"message": "Image uploaded"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
