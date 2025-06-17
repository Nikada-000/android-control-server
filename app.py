from flask import Flask, request, jsonify, Response, send_from_directory
from datetime import datetime
from flask_cors import CORS
import os
import cv2

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

@app.route("/", methods=["GET"])
def home():
    return "✅ Android Control Server is running."

@app.route("/command", methods=["POST"])
def send_command():
    data = request.json
    device_id = data.get("device_id")
    command = data.get("command")

    device = next((d for d in devices if d["device_id"] == device_id), None)
    if not device:
        return jsonify({"error": "Device not found"}), 404

    print(f"📤 Command '{command}' sent to {device_id}")
    return jsonify({"message": f"Command '{command}' sent to {device_id}"})

# === Live camera stream ===
camera = cv2.VideoCapture(0)

def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/stream')
def video_stream():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stream_page')
def stream_page():
    return '''
    <html>
    <head><title>Live Camera</title></head>
    <body>
        <h1>Live Camera Stream</h1>
        <img src="/stream" width="640" height="480">
    </body>
    </html>
    '''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
