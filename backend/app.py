from flask import Flask, jsonify, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)
# Axial hex directions (q, r)
HEX_DIRECTIONS = [
    (1, 0), (1, -1), (0, -1),
    (-1, 0), (-1, 1), (0, 1)
]

# --- Resources & Building Requirements ---
RESOURCE_POOL = [
    "Iron", "Crystal", "Gas", "Ice", "Silver", "Algae",
    "Silicon", "Copper", "Sand", "Carbon", "Nickel", "Stone",
    "Obsidian", "Quartz", "Dust", "Water", "Oil", "Fish",
    "Plasma", "Fungus", "Xenonite", "Ore", "SpaceDust", "Fuel"
]

BUILDING_REQUIREMENTS = {
    "Collector": {"Silver": 2, "Ore": 1},
    "Factory": {"Algae": 2, "SpaceDust": 3},
    "Settlement": {"Fungus": 4},
    "Fuel Pump": {"Ore": 2, "Crystal": 1},
    "Scanner": {"Ore": 1, "Silicon": 1}
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

time_tick = 0
MOVE_COST_SAME_BODY = 1
MOVE_COST_DIFFERENT_BODY = 5

def are_adjacent(s1, s2):
    dq = s1["q"] - s2["q"]
    dr = s1["r"] - s2["r"]
    ds = -(s1["q"] + s1["r"]) - (-(s2["q"] + s2["r"]))
    return abs(dq) <= 1 and abs(dr) <= 1 and abs(ds) <= 1


def get_body_of_space(space_id):
    for body in system["bodies"]:
        for space in body["spaces"]:
            if space["id"] == space_id:
                return body
    return None

def generate_space(name_prefix, q, r):
    global space_id_counter
    space = {
        "id": space_id_counter,
        "name": f"{name_prefix} - Space {space_id_counter}",
        "items": random.sample(RESOURCE_POOL, 3),
        "building": None,
        "q": q,
        "r": r
    }
    space_id_counter += 1
    return space

def generate_bodies():
    bodies = []
    for body_name, space_count in BODY_DEFINITIONS:
        body = {
            "id": len(bodies) + 1,
            "name": body_name,
            "spaces": []
        }

        # Place tiles using a spiral hex pattern
        layers = 0
        while 3 * layers * (layers + 1) + 1 < space_count:
            layers += 1

        placed = 0
        for q in range(-layers, layers + 1):
            for r in range(-layers, layers + 1):
                s = -q - r
                if abs(s) > layers:
                    continue
                if placed >= space_count:
                    break
                space = generate_space(body_name, q, r)
                body["spaces"].append(space)
                placed += 1

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
    "inventory": [],
    "explored_spaces": []
}
unit["inventory"].append("Robot")
unit["inventory"].append("Algae")
unit["inventory"].append("Algae")
unit["inventory"].append("Algae")
unit["inventory"].append("SpaceDust")
unit["inventory"].append("SpaceDust")
unit["inventory"].append("SpaceDust")

robots = []  # Each robot is a dict with position, collected items, mode, etc.

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

def get_neighbors_within_radius(center_space, body, radius):
    q0, r0 = center_space["q"], center_space["r"]
    return [
        s for s in body["spaces"]
        if max(abs(s["q"] - q0), abs(s["r"] - r0), abs((-s["q"] - s["r"]) - (-q0 - r0))) <= radius
    ]


# --- Routes ---
@app.route('/api/system')
def get_system():
	return jsonify({"system": system, "robots": robots})

@app.route('/api/unit', methods=['GET'])
def get_unit():
    return jsonify(unit)

@app.route('/api/move_unit', methods=['POST'])
def move_unit():
    target_id = request.json.get("space_id")
    target_space = get_space_by_id(target_id)
    if not target_space:
        return jsonify(unit)

    current_space = get_space_by_id(unit["current_space_id"])
    target_body = get_body_of_space(target_id)
    current_body = get_body_of_space(current_space["id"])
    unit["current_space_id"] = target_id
    if target_id not in unit["explored_spaces"]:
        unit["explored_spaces"].append(target_id)


    # Same-body movement must be adjacent
    if target_body["id"] == current_body["id"]:
        if not are_adjacent(current_space, target_space):
            return jsonify({"error": "Can only move to adjacent space"}), 400
        cost = 1
    else:
        cost = MOVE_COST_DIFFERENT_BODY

    if unit["inventory"].count("Fuel") < cost:
        return jsonify({"error": "Not enough fuel"}), 400

    for _ in range(cost):
        unit["inventory"].remove("Fuel")

    unit["current_space_id"] = target_id
    return jsonify(unit)



@app.route('/api/collect_item', methods=['POST'])
def collect_item():
    item_name = request.json.get("item")
    space = get_space_by_id(unit["current_space_id"])

    if not space:
        return jsonify(unit)

    if item_name == "Robot":
        if space.get("factory_robots", 0) > 0:
            space["factory_robots"] -= 1
            unit["inventory"].append("Robot")
    elif item_name in space["items"]:
        space["items"].remove(item_name)
        unit["inventory"].append(item_name)

    return jsonify(unit)

@app.route('/api/deploy_robot', methods=['POST'])
def deploy_robot():
    space_id = request.json.get("space_id")
    space = get_space_by_id(space_id)
    body = get_body_of_space(space_id)

    if unit["inventory"].count("Robot") == 0:
        return jsonify({"error": "No robots to deploy"}), 400

    if space and body:
        unit["inventory"].remove("Robot")
        robots.append({
            "current_space_id": space["id"],
            "current_body_id": body["id"],
            "collected_items": [],
            "mode": "explore",
            "turns_since_action": 0
        })

    return jsonify({"unit": unit, "system": system})



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
    if building_name == "Scanner":
        body = get_body_of_space(space["id"])
        for neighbor in get_neighbors_within_radius(space, body, radius=2):
            if neighbor["id"] not in unit["explored_spaces"]:
                unit["explored_spaces"].append(neighbor["id"])


    return jsonify({"success": True, "space": space, "unit": unit})

@app.route('/api/advance_time', methods=['POST'])
def advance_time():
	global time_tick
	time_tick += 1

	# Solar Generator
	unit["inventory"].append("Fuel")

	print(f"\n[TURN {time_tick}] ROBOT SUMMARY:")
	for i, robot in enumerate(robots):
		print(f" - Robot {i}:")
		print(f"     Pos: Body {robot['current_body_id']}, Space {robot['current_space_id']}")
		print(f"     Items: {robot['collected_items']}")
		print(f"     Mode: {robot['mode']}")

	# Add fuel from fuel pumps
	for body in system["bodies"]:
		for space in body["spaces"]:
			if space.get("building") == "Fuel Pump":
				if space["items"].count("Fuel") < 5:
					space["items"].append("Fuel")

	# Generate robots in factories
	for body in system["bodies"]:
		for space in body["spaces"]:
			if space.get("building") == "Factory":
				if "factory_robots" not in space:
					space["factory_robots"] = 0
				if space["factory_robots"] < 3:
					space["factory_robots"] += 1

	# --- Robot Logic ---
	for robot in robots:
		# Locate robot's current space and body
		body = next((b for b in system["bodies"] if b["id"] == robot["current_body_id"]), None)
		if not body:
			continue
		space = next((s for s in body["spaces"] if s["id"] == robot["current_space_id"]), None)
		if not space:
			continue

		# Mark space as explored
		if space["id"] not in unit["explored_spaces"]:
			unit["explored_spaces"].append(space["id"])

		# DEPOSIT MODE: If robot is full and at a Factory, deposit items
		if len(robot["collected_items"]) >= 2 and space.get("building") == "Factory":
			if "items" not in space:
				space["items"] = []
			space["items"].extend(robot["collected_items"])
			robot["collected_items"] = []
			continue  # Robot stays put this turn

		# COLLECTION MODE: Try to collect
		if len(robot["collected_items"]) < 2 and space.get("items"):
			while len(robot["collected_items"]) < 2 and space["items"]:
				robot["collected_items"].append(space["items"].pop())
			continue  # Stay here this turn

		# MOVEMENT: Decide target
		target_space = None

		if len(robot["collected_items"]) >= 2:
			# Try to move toward a factory
			factories = [
				s for s in body["spaces"]
				if s.get("building") == "Factory"
			]
			if factories:
				# Pick the closest factory (currently naive approach: first match)
				factory = factories[0]
				dq = factory["q"] - space["q"]
				dr = factory["r"] - space["r"]
				# Find direction that minimizes distance
				best_dir = min(HEX_DIRECTIONS, key=lambda d: abs(d[0] - dq) + abs(d[1] - dr))
				new_q = space["q"] + best_dir[0]
				new_r = space["r"] + best_dir[1]
				target_space = next((s for s in body["spaces"] if s["q"] == new_q and s["r"] == new_r), None)

		else:
			# Otherwise move randomly
			dir = random.choice(HEX_DIRECTIONS)
			new_q = space["q"] + dir[0]
			new_r = space["r"] + dir[1]
			target_space = next((s for s in body["spaces"] if s["q"] == new_q and s["r"] == new_r), None)

		# Move robot
		if target_space:
			robot["current_space_id"] = target_space["id"]
			if target_space["id"] not in unit["explored_spaces"]:
				unit["explored_spaces"].append(target_space["id"])

	return jsonify({"time": time_tick, "unit": unit, "system": system, "robots": robots})

if __name__ == '__main__':
    app.run(debug=True)
