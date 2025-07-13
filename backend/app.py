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
from utils.resource_management import get_named_inventory
from utils.location_management import hex_distance, are_adjacent_coords, space_distance, are_adjacent_spaces, estimate_body_radius

app = Flask(__name__)
CORS(app)

game_state = GameState()

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
        game_state.resources[resource.id] = resource
    return resource_list

RESOURCE_NAMES = [
    "Iron", "Crystal", "Gas", "Ice", "Silver", "Algae",
    "Silicon", "Copper", "Sand", "Carbon", "Nickel", "Stone",
    "Obsidian", "Quartz", "Dust", "Water", "Oil", "Fish",
    "Plasma", "Fungus", "Xenonite", "Ore", "SpaceDust"
]

RESOURCE_POOL = generate_resource_pool(RESOURCE_NAMES)

#Add fuel
FUEL_ID = 'fuel'
FuelResource = Resource(id=FUEL_ID,name='Fuel',properties={})
RESOURCE_POOL.append(FuelResource)
game_state.resources[FUEL_ID] = FuelResource
#FUEL_ID = next((res.id for res in RESOURCE_POOL if res.name == "Fuel"), None)

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

def generate_space_id(body, rel_q, rel_r):
    return f"body:{body.id}:{rel_q}:{rel_r}"

# --- Global Game State ---
# --- Game State & Ownership Setup ---

def get_starting_inventory():
    """Generate starting inventory with enough resources to build all structures"""
    # Resource requirements for all structures
    required_resources = {
        "Silver": 2,    # Collector
        "Algae": 2,     # Factory
        "Silicon": 1,   # Scanner
        "Fungus": 4,    # Settlement
        "Ore": 4,       # Collector (1) + FuelPump (2) + Scanner (1)
        "SpaceDust": 3, # Factory
        "Crystal": 1    # FuelPump
    }
    
    # Convert resource names to IDs using game state
    starting_inventory = {FUEL_ID: 10}  # Starting fuel
    
    for resource_name, quantity in required_resources.items():
        resource_id = game_state.find_resource_by_name(resource_name)
        if resource_id:
            starting_inventory[resource_id] = quantity
    
    return starting_inventory

player = Player(name="Player 1", description="The human player", player_id='player_1')
game_state.players[player.player_id] = player

# Create the player unit (after resources are loaded)
player_unit = PlayerUnit(id="u1", location_space_id=None)
player_unit.update_inventory(get_starting_inventory())

player.entities.append(player_unit)  # mark ownership
game_state.units[player_unit.id] = player_unit

robots = []
time_tick = 0

# --- World Generation ---
system = System(
    id=str(uuid.uuid4()),
    name="Eos System",
    q=0,
	r=0
)
game_state.systems[system.id]=system

def generate_system(system, player_unit, resource_pool, body_definitions):
	used_coords = set()
	radius_between_bodies = 2  # Extra spacing beyond footprint
	directions = HEX_DIRECTIONS

	def is_area_free(center_q, center_r, radius):
		for dq in range(-radius, radius + 1):
			for dr in range(max(-radius, -dq - radius), min(radius, -dq + radius) + 1):
				q, r = center_q + dq, center_r + dr
				if (q, r) in used_coords:
					return False
		return True

	def mark_area_used(center_q, center_r, radius):
		for dq in range(-radius, radius + 1):
			for dr in range(max(-radius, -dq - radius), min(radius, -dq + radius) + 1):
				q, r = center_q + dq, center_r + dr
				used_coords.add((q, r))

	def find_open_coord(required_radius):
		# Spiral out to find usable open body anchor
		for radius in range(1, 100):
			q, r = 0, -radius
			for direction in range(6):
				for _ in range(radius):
					dq, dr = directions[direction]
					cand_q, cand_r = q + random.choice([-1, 0, 1]), r + random.choice([-1, 0, 1])
					cand_q *= (required_radius + radius_between_bodies)
					cand_r *= (required_radius + radius_between_bodies)
					if is_area_free(cand_q, cand_r, required_radius + radius_between_bodies):
						mark_area_used(cand_q, cand_r, required_radius)
						return (cand_q, cand_r)
					q += dq
					r += dr
		raise Exception("Failed to find non-overlapping body location")

	for body_index, (body_name, space_count) in enumerate(body_definitions):
		body_radius = estimate_body_radius(space_count)
		body_q, body_r = find_open_coord(body_radius)

		body = Body(
			id=f"body_{body_index + 1}",
			system_id=system.id,
			name=body_name,
			q=body_q,
			r=body_r,
		)
		game_state.bodies[body.id] = body

		for i in range(space_count):

			next_q, next_r = body.get_next_space_coords()
			space_id = generate_space_id(body,next_q,next_r)
			space = Space(
				id=space_id,
				body_rel_q=next_q,
				body_rel_r=next_r,
				name=f"{body.name} - Space {i+1}",
				body_id=body.id,
				inventory={},
			)
			space.set_global_coords(body.q,body.r)

			# Populate inventory
			num_resources = random.randint(1, 4)
			selected = random.sample(resource_pool, num_resources)
			for resource in selected:
				space.inventory[resource.id] = space.inventory.get(resource.id, 0) + 1

			body.add_space(space)
			game_state.spaces[space.id] = space
			
			# Make the first space of each body system-wide accessible
			if i == 0:  # First space (center space)
				game_state.add_system_wide_accessible_space(space.id)

		system.bodies.append(body)

	# Place unit at first space
	if system.bodies and system.bodies[0].spaces:
		player_unit.location_space_id = system.bodies[0].spaces[0].id
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
def find_resource_id_by_name(resource_name):
    """Convert resource name to resource ID - deprecated, use game_state.find_resource_by_name()"""
    return game_state.find_resource_by_name(resource_name)

def find_space(space_id):
    return game_state.get_space_by_id(space_id)

def find_body_by_space(space_id):
    space = game_state.get_space_by_id(space_id)
    if space and space.body_id:
        return game_state.get_body_by_id(space.body_id)
    return None

def find_unit(unit_id=None, unit_name=None):
	if unit_id and unit_id in game_state.units:
		return game_state.units[unit_id]
	if unit_name:
		for u in game_state.units.values():
			if u.name.lower() == unit_name.lower():
				return u
	return None

def find_player_units(player_id):
    results = []
    p = game_state.get_player_by_id(player_id)
    for e in p.entities:
        if isinstance(e, PlayerUnit):
            results.append(e.to_dict(game_state=game_state))
    return jsonify(results)


# --- Routes ---
@app.route('/api/system')
def get_system():
    return jsonify(system.to_dict_details(game_state=game_state))

@app.route('/api/game_state')
def get_game_state():
    return jsonify(game_state.to_dict())

@app.route("/api/player_units/<player_id>")
def api_find_player_units(player_id):
    return find_player_units(player_id)


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
    direction = data.get("direction")
    target_space_id = data.get("space_id")  # For direct space movement

    unit = game_state.get_unit_by_id(unit_id)
    if not unit or not isinstance(unit, PlayerUnit):
        return jsonify({"error": "Unit not found"}), 404

    current_space = game_state.get_space_by_id(unit.location_space_id)
    if not current_space:
        return jsonify({"error": "Current space not found"}), 400

    # Handle direct space movement (inter-body movement)
    if target_space_id:
        destination = game_state.get_space_by_id(target_space_id)
        if not destination:
            return jsonify({"error": "Target space not found"}), 400
        
        print("\n=== DIRECT MOVE DEBUG ===")
        print(f"Current space: {current_space.id}")
        print(f"Target space: {target_space_id}")
        print("=========================")
        
    # Handle directional movement (same body movement)
    elif direction is not None:
        unit.direction = direction  # Update direction on the unit
        
        # Axial offset for this direction
        dq, dr = HEX_DIRECTIONS[direction]
        dest_q = current_space.body_rel_q + dq
        dest_r = current_space.body_rel_r + dr

        # Find target space in same body
        destination_id = generate_space_id( game_state.get_body_by_id(current_space.body_id), dest_q, dest_r)
        destination = game_state.get_space_by_id(destination_id)

        print("\n=== DIRECTIONAL MOVE DEBUG ===")
        print(f"Current space: {current_space.id}")
        print(f"Direction: {direction}")
        print(f"Offset: dq={dq}, dr={dr}")
        print(f"Target rel coords: {dest_q}, {dest_r}")
        print(f"Target id: {destination_id}")
        print("==============================")

        if not destination:
            return jsonify({"error": "No space in that direction"}), 400
    else:
        return jsonify({"error": "Must provide either direction or space_id"}), 400

    # Perform the move via the ability system
    result = player.perform_unit_ability(
        actor_id=unit.id,
        game_state=game_state,
        ability="move",
        space_id=destination.id
    )

    if result:  # e.g. "not enough fuel", "too far", etc.
        print("MoveAbility returned error:", result)
        return jsonify({"error": result}), 400

    return jsonify(unit.to_dict())


@app.route('/api/collect_item', methods=['POST'])
def collect_item():
	data = request.json
	unit = find_unit(data.get("unit_id"), data.get("unit_name"))
	space = find_space(data.get("space_id")) if data.get("space_id") else find_space(unit.location_space_id)
	resource_input = data.get("resource_id")
	quantity = data.get("quantity")
	structure_id = data.get("structure_id")

	if not unit:
		return jsonify({"error": "Unit not found"}), 404
	if not resource_input:
		return jsonify({"error": "Missing resource_id"}), 400
	if not space:
		return jsonify({"error": "Space not found"}), 404

	# Convert resource name to ID if needed
	resource_id = find_resource_id_by_name(resource_input)
	if not resource_id:
		# Maybe it's already an ID, try using it directly
		resource_id = resource_input

	# If collecting from structure, collect from structure inventory
	if structure_id:
		structure = game_state.get_structure_by_id(structure_id)
		if not structure:
			return jsonify({"error": "Structure not found"}), 404
		
		available = structure.inventory.get(resource_id, 0)
		if available <= 0:
			return jsonify({"error": f"No {resource_input} available in structure"}), 400

		take = min(quantity or available, available)
		structure.update_inventory({resource_id: -take})
		unit.update_inventory({resource_id: take})
		
		result = f"Collected {take} x {resource_input} from {structure.name}."
	else:
		# Collect from space using existing ability system
		result = player.perform_unit_ability(
			actor_id=unit.id,
			game_state=game_state,
			ability="collect",
			resource_id=resource_id,
			quantity=quantity
		)

	return jsonify({
		"result": result,
		"unit": unit.to_dict(game_state=game_state),
		"space": space.to_dict(game_state=game_state)
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
	resource_cost_names = STRUCTURE_REQUIREMENTS.get(structure_type)
	if not resource_cost_names:
		return jsonify({"error": f"Unknown structure type: {structure_type}"}), 400

	structure_cls = get_structure_class_by_type(structure_type)
	if not structure_cls:
		return jsonify({"error": f"No class found for structure: {structure_type}"}), 400

	# Convert resource names to IDs for BuildAbility
	resource_cost = {}
	for resource_name, quantity in resource_cost_names.items():
		resource_id = game_state.find_resource_by_name(resource_name)
		if resource_id:
			resource_cost[resource_id] = quantity

	# Perform the build using the unit's BuildAbility
	result = player.perform_unit_ability(
		actor_id=unit.id,
		game_state=game_state,
		ability="build",
		structure_type=structure_type,
		resource_cost=resource_cost
	)

	# Handle structured result or error message
	if isinstance(result, str) and (result.startswith("Cannot build") or result.startswith("Insufficient")):
		return jsonify({"error": result}), 400

	space = find_space(unit.location_space_id)
	return jsonify({
		"result": result,
		"unit": unit.to_dict(game_state=game_state),
		"space": space.to_dict(game_state=game_state)
	})

@app.route('/api/movement_options', methods=['GET'])
def get_movement_options():
    unit_id = request.args.get("unit_id")
    
    if not unit_id:
        return jsonify({"error": "Missing unit_id"}), 400
    
    unit = game_state.get_unit_by_id(unit_id)
    if not unit:
        return jsonify({"error": "Unit not found"}), 404
    
    current_fuel = unit.inventory.get(FUEL_ID, 0)
    current_space = game_state.get_space_by_id(unit.location_space_id)
    
    if not current_space:
        return jsonify({"error": "Current space not found"}), 400
    
    # Get all bodies except current one
    current_body_id = current_space.body_id
    reachable_bodies = []
    
    for body in game_state.bodies.values():
        if body.id == current_body_id:
            continue  # Skip current body
            
        # Get explored spaces on this body (unit-explored + system-wide accessible)
        explored_spaces = []
        accessible_space_ids = game_state.get_all_accessible_spaces_for_unit(unit)
        
        for space in body.spaces:
            if space.id in accessible_space_ids:
                explored_spaces.append({
                    "space_id": space.id,
                    "name": space.name,
                    "q": space.q,
                    "r": space.r,
                    "named_inventory": get_named_inventory(space.inventory, game_state)
                })
        
        # Only include bodies with explored spaces
        if explored_spaces:
            reachable_bodies.append({
                "body_id": body.id,
                "name": body.name,
                "fuel_cost": 5,  # Inter-body movement cost
                "explored_spaces": explored_spaces
            })
    
    return jsonify({
        "reachable_bodies": reachable_bodies,
        "current_fuel": current_fuel,
        "inter_body_cost": 5
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
