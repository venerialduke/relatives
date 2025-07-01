from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# --- Resources & Building Requirements ---
RESOURCE_POOL = [
    "Iron", "Crystal", "Gas", "Ice", "Silver", "Algae",
    "Silicon", "Copper", "Sand", "Carbon", "Nickel", "Stone",
    "Obsidian", "Quartz", "Dust", "Water", "Oil", "Fish",
    "Plasma", "Fungus", "Xenonite", "Ore", "SpaceDust"
]

BUILDING_REQUIREMENTS = {
    "Collector": {"Silver": 2, "Ore": 1},
    "Factory": {"Algae": 2, "SpaceDust": 3},
    "Settlement": {"Fungus": 4}
}

BODY_DEFINITIONS = [
    ("Planet 1", 20),
    ("Planet 2", 35),
    ("Planet 3", 30),
    ("Asteroid Clump", 10),
    ("Moon 1", 15),
    ("Comet", 10),
    ("Planet 4", 50)
]

space_id_counter = 1

def generate_space(name_prefix):
    global space_id_counter
    space = {
        "id": space_id_counter,
        "name": f"{name_prefix} - Space {space_id_counter}",
        "items": random.sample(RESOURCE_POOL, 3),
        "building": None
    }
    space_id_counter += 1
    return space

def generate_bodies():
    bodies = []
    for body_name, space_count in BODY_DEFINITIONS:
        body = {
            "id": len(bodies) + 1,
            "name": body_name,
            "spaces": [generate_space(body_name) for _ in range(space_count)]
        }
        bodies.append(body)
    return bodies

system = {
    "id": 1,
    "name": "Eos System",
    "bodies": generate_bodies()
}

unit = {
    "id": 1,
    "current_space_id": 1,
    "inventory": []
}

def get_space_by_id(space_id):
    for body in system["bodies"]:
        for space in body["spaces"]:
            if space["id"] == space_id:
                return space
    return None

def has_required_resources(inventory, cost_dict):
    inventory_copy = inventory.copy()
    for res, amt in cost_dict.items():
        if inventory_copy.count(res) < amt:
            return False
    return True

def deduct_resources(inventory, cost_dict):
    for res, amt in cost_dict.items():
        for _ in range(amt):
            inventory.remove(res)

# --- Routes ---
@app.route('/api/system', methods=['GET'])
def get_system():
    return jsonify(system)

@app.route('/api/unit', methods=['GET'])
def get_unit():
    return jsonify(unit)

@app.route('/api/move_unit', methods=['POST'])
def move_unit():
    target_id = request.json.get("space_id")
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

@app.route('/api/build_building', methods=['POST'])
def build_building():
    data = request.json
    building_name = data.get("building")
    space = get_space_by_id(unit["current_space_id"])

    if not space or not building_name:
        return jsonify({"error": "Invalid request"}), 400

    if space["building"] is not None:
        return jsonify({"error": "Space already has a building"}), 400

    requirements = BUILDING_REQUIREMENTS.get(building_name)
    if not requirements:
        return jsonify({"error": "Unknown building type"}), 400

    if not has_required_resources(unit["inventory"], requirements):
        return jsonify({"error": "Not enough resources"}), 400

    deduct_resources(unit["inventory"], requirements)
    space["building"] = building_name

    return jsonify({"success": True, "space": space, "unit": unit})

if __name__ == '__main__':
    app.run(debug=True)
