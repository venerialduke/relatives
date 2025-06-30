from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- In-memory data for simplicity ---
system = {
    "id": 1,
    "name": "Alpha System",
    "spaces": [
        {"id": 1, "name": "Crater Base", "items": ["Iron", "Crystal", "Gas"]},
        {"id": 2, "name": "Frozen Ridge", "items": ["Ice", "Silver", "Algae"]},
        {"id": 3, "name": "Dusty Dunes", "items": ["Silicon", "Copper", "Sand"]}
    ]
}

unit = {
    "id": 1,
    "current_space_id": 1,
    "inventory": []
}

# --- Routes ---

@app.route('/api/system', methods=['GET'])
def get_system():
    return jsonify(system)

@app.route('/api/unit', methods=['GET'])
def get_unit():
    return jsonify(unit)

@app.route('/api/move_unit', methods=['POST'])
def move_unit():
    data = request.json
    target_id = data.get("space_id")
    unit["current_space_id"] = target_id
    return jsonify(unit)

@app.route('/api/collect_item', methods=['POST'])
def collect_item():
    data = request.json
    space_id = unit["current_space_id"]
    item_name = data.get("item")

    for space in system["spaces"]:
        if space["id"] == space_id and item_name in space["items"]:
            space["items"].remove(item_name)
            unit["inventory"].append(item_name)
            break
    return jsonify(unit)

if __name__ == '__main__':
    app.run(debug=True)
