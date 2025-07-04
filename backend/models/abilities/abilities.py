# abilities.py
from models.abilities.base import Ability

class CollectAbility(Ability):
	def __init__(self):
		super().__init__("collect", "Collects a specific resource from the current space.")

	def perform(self, actor, game_state, **kwargs):
		resource_id = kwargs.get("resource_id")
		if not resource_id:
			return "No resource specified."

		space = game_state.get_space_by_id(actor.location_space_id)
		if not space or not space.inventory:
			return "Nothing to collect."

		available = space.inventory.get(resource_id, 0)
		if available <= 0:
			return f"No {resource_id} available to collect."

		take = kwargs.get("quantity", available)  # Optional limit
		take = min(take, available)

		space.update_inventory({resource_id: -take})
		actor.update_inventory({resource_id: take})

		return f"Collected {take} x {resource_id}."

class ScanAbility(Ability):
	def __init__(self):
		super().__init__("scan", "Reveals nearby spaces (radius 2).")

	def perform(self, actor, game_state, **kwargs):
		current_space = game_state.get_space_by_id(actor.location_space_id)
		body = game_state.get_body_by_id(current_space.body_id)
		nearby = game_state.get_spaces_in_radius(body, current_space.location, radius=2)
		for space in nearby:
			actor.explored_spaces.add(space.id)
		return f"Scanned {len(nearby)} spaces."


class DeployAbility(Ability):
	def __init__(self):
		super().__init__("deploy", "Deploys a robot or unit to a nearby space.")

	def perform(self, actor, game_state, **kwargs):
		target_space_id = kwargs.get("target_space_id")
		robot = kwargs.get("unit")

		if not target_space_id or not robot:
			return "Invalid deployment parameters."

		target_space = game_state.get_space_by_id(target_space_id)
		if len(target_space.units) >= target_space.max_units:
			return "Target space full."

		# Move the robot
		robot.location_space_id = target_space.id
		target_space.units.append(robot)
		return f"Deployed {robot.name} to space {target_space.id}."


class BuildAbility(Ability):
	def __init__(self):
		super().__init__("build", "Constructs a structure on this space using resources.")

	def perform(self, actor, game_state, **kwargs):
		structure_type = kwargs.get("structure_type")
		resource_cost = kwargs.get("resource_cost", {})  # {"algae": 2, "ore": 1}
		current_space = game_state.get_space_by_id(actor.location_space_id)

		if len(current_space.structures) >= current_space.max_buildings:
			return "Cannot build — building slot full."

		# Check resources
		for res, amt in resource_cost.items():
			if actor.inventory.get(res, 0) < amt:
				return f"Insufficient resources: need {res} x{amt}"

		# Spend resources
		actor.update_inventory( {k: -v for k, v in resource_cost.items()} )

		# Build
		structure = game_state.build_structure(structure_type, location_space_id=current_space.id)
		current_space.structures.append(structure)
		return f"Built {structure_type} on space {current_space.id}."
