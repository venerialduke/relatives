from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- In-memory data: Systems → Bodies → Spaces ---
system = {
    "id": 1,
    "name": "Alpha System",
    "bodies": [
        {
            "id": 1,
            "name": "Crater Moon",
            "spaces": [
                {"id": 1, "name": "Crater Base", "items": ["Iron", "Crystal", "Gas"]},
                {"id": 2, "name": "Shattered Rim", "items": ["Obsidian", "Quartz", "Dust"]}
            ]
        },
        {
            "id": 2,
            "name": "Frozen Planet",
            "spaces": [
                {"id": 3, "name": "Glacial Cliff", "items": ["Ice", "Silver", "Algae"]},
                {"id": 4, "name": "Polar Bay", "items": ["Water", "Oil", "Fish"]}
            ]
        },
        {
            "id": 3,
            "name": "Dusty Rock",
            "spaces": [
                {"id": 5, "name": "Red Ridge", "items": ["Silicon", "Copper", "Sand"]},
                {"id": 6, "name": "Old Crater", "items": ["Carbon", "Nickel", "Stone"]}
            ]
        }
    ]
}

unit = {
    "id": 1,
    "current_space_id": 1,
    "inventory": []
}

# --- Helper to find a space by id ---
def get_space_by_id(space_id):
    for body in system["bodies"]:
        for space in body["spaces"]:
            if space["id"] == space_id:
                return space
    return None

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
    if get_space_by_id(target_id):
        unit["current_space_id"] = target_id
    return jsonify(unit)

@app.route('/api/collect_item', methods=['POST'])
def collect_item():
    item_name = request.json.get("item")
    space = get_space_by_id(unit["current_space_id"])
    if space and item_name in space["items"]:
        space["items"].remove(item_name)
        unit["inventory"].append(item_name)
    return jsonify(unit)

if __name__ == '__main__':
    app.run(debug=True)
