from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory device store (for demo)
devices = []

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    device_id = data.get("device_id")
    
    # Check if device already exists
    existing = next((d for d in devices if d["device_id"] == device_id), None)
    if not existing:
        devices.append(data)
    else:
        # Update existing device data
        existing.update(data)

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
    return jsonify({"message": f"Command '{command}' sent to {device_id}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # default to 5000 if PORT is not set
    app.run(host="0.0.0.0", port=port)
