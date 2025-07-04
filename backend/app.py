from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import uuid
import random

from models.entities.entities import Structure, Resource
from models.containers.containers import Space, Body, System
from models.gamemonitors.monitors import GameState
from models.gameowners.owners import Player
from models.abilities.abilities import MoveAbility,CollectAbility,BuildAbility
from models.entities.structure_map import get_structure_class_by_type, STRUCTURE_CLS_MAP
from models.entities.entity_content import PlayerUnit

from utils.location_management import hex_distance, are_adjacent_coords, space_distance, are_adjacent_spaces

app = Flask(__name__)
CORS(app)

# --- Constants ---
def generate_resource_pool(input_resource_map):
    resource_list = []
    for idx, name in enumerate(input_resource_map):
        resource = Resource(
            id=f"res_{idx+1}",
            name=name,
            properties={}
        )
        resource_list.append(resource)
    return resource_list

RESOURCE_NAMES = [
    "Iron", "Crystal", "Gas", "Ice", "Silver", "Algae",
    "Silicon", "Copper", "Sand", "Carbon", "Nickel", "Stone",
    "Obsidian", "Quartz", "Dust", "Water", "Oil", "Fish",
    "Plasma", "Fungus", "Xenonite", "Ore", "SpaceDust", "Fuel"
]

RESOURCE_POOL = generate_resource_pool(RESOURCE_NAMES)

STRUCTURE_REQUIREMENTS = {
    "Collector": {"Silver": 2, "Ore": 1},
    "Factory": {"Algae": 2, "SpaceDust": 3},
    "Settlement": {"Fungus": 4},
    "FuelPump": {"Ore": 2, "Crystal": 1},
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

HEX_DIRECTIONS = [
    (1, 0), (1, -1), (0, -1),
    (-1, 0), (-1, 1), (0, 1)
]

# --- Global Game State ---
# --- Game State & Ownership Setup ---
game_state = GameState()
player = Player(name="Player 1", description="The human player")

# Create the player unit
player_unit = PlayerUnit(id="u1", location_space_id=None)
player_unit.update_inventory({"Fuel": 10})
player.entities.append(player_unit)  # mark ownership
game_state.units[player_unit.id] = player_unit

robots = []
time_tick = 0

# --- World Generation ---
system = System(
    id=str(uuid.uuid4()),
    name="Eos System",
    location=(0, 0)  # or whatever default location you want
)
game_state.systems[system.id]=system

def generate_system(system, player_unit, resource_pool, body_definitions):
	for body_index, (body_name, space_count) in enumerate(body_definitions):
		body = Body(
			id=f"body_{body_index + 1}",
			system_id=system.id,
			name=body_name,
			location=(random.randint(-10, 10), random.randint(-10, 10))
		)
		game_state.bodies[body.id] = body

		for i in range(space_count):
			space_id = str(uuid.uuid4())
			space_name = f"{body.name} - Space {i+1}"
			space_location = (0, 0)  # placeholder; real layout via q/r

			space = Space(
				id=space_id,
				name=space_name,
				location=space_location,
				body_id=body.id,
				inventory={},
			)

			# Populate inventory
			num_resources = random.randint(1, 4)
			selected = random.sample(resource_pool, num_resources)
			for resource in selected:
				space.inventory[resource.id] = space.inventory.get(resource.id, 0) + 1

			# Add to body and game state
			body.add_space(space)
			game_state.spaces[space.id] = space

		system.bodies.append(body)

	# Place unit at first space
	if system.bodies and system.bodies[0].spaces:
		player_unit.current_space_id = system.bodies[0].spaces[0].id
	else:
		raise ValueError("No spaces created; can't place unit.")

	return system


system = generate_system(
    system=system,
    player_unit=player_unit,
    resource_pool=RESOURCE_POOL,
    body_definitions=BODY_DEFINITIONS
)


# --- Helper Functions ---
def find_space(space_id):
    return system.get_space_by_id(space_id)

def find_body_by_space(space_id):
    return system.get_body_of_space(space_id)

def find_unit(unit_id=None, unit_name=None):
	if unit_id and unit_id in game_state.units:
		return game_state.units[unit_id]
	if unit_name:
		for u in game_state.units.values():
			if u.name.lower() == unit_name.lower():
				return u
	return None

# --- Routes ---
@app.route('/api/system')
def get_system():
    return jsonify(system.to_dict())

@app.route('/api/unit')
def get_unit():
	unit_id = request.args.get("unit_id")
	unit_name = request.args.get("unit_name")

	unit = find_unit(unit_id=unit_id, unit_name=unit_name)
	if unit:
		return jsonify(unit.to_dict())

	return jsonify({"error": "Unit not found"}), 404


@app.route('/api/move_unit', methods=['POST'])
def move_unit():
	data = request.json
	unit_id = data.get("unit_id")
	unit_name = data.get("unit_name")
	space_id = data.get("space_id")

	unit = find_unit(unit_id, unit_name)
	if not unit:
		return jsonify({"error": "Unit not found"}), 404

	target = find_space(space_id)
	if not target:
		return jsonify({"error": "Target space not found"}), 400

	# Now we let the ability system handle all internal checks
	result = player.perform_unit_ability(
		actor_id=unit.id,
		game_state=game_state,
		ability="move",
		space_id=space_id  # <- passed into MoveAbility.perform()
	)

	if result:  # Any non-None return is treated as an error
		return jsonify({"error": result}), 400

	return jsonify(unit.to_dict())


@app.route('/api/collect_item', methods=['POST'])
def collect_item():
	data = request.json
	unit = find_unit(data.get("unit_id"), data.get("unit_name"))
	space = find_space(data.get("space_id")) if data.get("space_id") else find_space(unit.current_space_id)
	resource_id = data.get("resource_id")
	quantity = data.get("quantity")

	if not unit:
		return jsonify({"error": "Unit not found"}), 404
	if not resource_id:
		return jsonify({"error": "Missing resource_id"}), 400
	if not space:
		return jsonify({"error": "Space not found"}), 404

	result = player.perform_unit_ability(
		actor_id=unit.id,
		game_state=game_state,
		ability="collect",
		resource_id=resource_id,
		quantity=quantity
	)

	return jsonify({
		"result": result,
		"unit": unit.to_dict(),
		"space": space.to_dict()
	})

@app.route('/api/build_structure', methods=['POST'])
def build_structure():
	data = request.json
	structure_type = data.get("structure_type")  # "Factory", "Collector", etc.
	unit = find_unit(data.get("unit_id"), data.get("unit_name"))

	if not unit:
		return jsonify({"error": "Unit not found"}), 404
	if not structure_type:
		return jsonify({"error": "Missing structure type"}), 400

	# Cost + class lookup
	resource_cost = STRUCTURE_REQUIREMENTS.get(structure_type)
	if not resource_cost:
		return jsonify({"error": f"Unknown structure type: {structure_type}"}), 400

	structure_cls = get_structure_class_by_type(structure_type)
	if not structure_cls:
		return jsonify({"error": f"No class found for structure: {structure_type}"}), 400

	# Create structure instance (but only *after* validation passes inside BuildAbility)
	structure_id = f"struct_{uuid.uuid4().hex[:8]}"
	location_space_id = unit.current_space_id
	structure_instance = structure_cls(id=structure_id, location_space_id=location_space_id)

	# Perform the build using the unit's BuildAbility
	result = player.perform_unit_ability(
		actor_id=unit.id,
		game_state=game_state,
		ability="build",
		structure=structure_instance,
		resource_cost=resource_cost
	)

	# Handle structured result or error message
	if isinstance(result, str) and (result.startswith("Cannot build") or result.startswith("Insufficient")):
		return jsonify({"error": result}), 400

	space = find_space(unit.current_space_id)
	return jsonify({
		"result": result,
		"unit": unit.to_dict(),
		"space": space.to_dict()
	})

@app.route('/api/advance_time', methods=['POST'])
def advance_time():
    global time_tick
    time_tick += 1

    # Advance time for all units
    for unit in game_state.units.values():
        unit.advance_time(game_state)

    # Advance time for all structures
    for structure in game_state.structures.values():
        structure.advance_time(game_state)

    # Advance time for all spaces
    for space in game_state.spaces.values():
        space.advance_time(game_state)

    # Advance time for all bodies
    for body in game_state.bodies.values():
        body.advance_time(game_state)

    # Advance time for all systems
    for system in game_state.systems.values():
        system.advance_time(game_state)

    return jsonify({
        "time": time_tick,
        "units": [unit.to_dict() for unit in game_state.units.values()],
        "systems": [system.to_dict() for system in game_state.systems.values()]
    })

if __name__ == '__main__':
    app.run(debug=True)
