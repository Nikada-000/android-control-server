from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

COMMAND_FILE = 'commands.json'

# Load commands if they exist
if not os.path.exists(COMMAND_FILE):
    with open(COMMAND_FILE, 'w') as f:
        json.dump({}, f)

def load_commands():
    with open(COMMAND_FILE, 'r') as f:
        return json.load(f)

def save_commands(data):
    with open(COMMAND_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    return "✅ Android Remote Command Server is Running"

@app.route('/register', methods=['POST'])
def register():
    device_id = request.json.get('device_id')
    if not device_id:
        return jsonify({"error": "Missing device_id"}), 400

    commands = load_commands()
    if device_id not in commands:
        commands[device_id] = {"command": "none"}
        save_commands(commands)
    return jsonify({"status": "registered", "device_id": device_id})

@app.route('/command/<device_id>', methods=['GET', 'POST'])
def command(device_id):
    commands = load_commands()

    if request.method == 'GET':
        cmd = commands.get(device_id, {"command": "none"})
        return jsonify(cmd)

    if request.method == 'POST':
        new_cmd = request.json.get('command')
        if not new_cmd:
            return jsonify({"error": "Missing command"}), 400
        commands[device_id] = {"command": new_cmd}
        save_commands(commands)
        return jsonify({"status": "command set", "command": new_cmd})

    return jsonify({"error": "Invalid request"}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

