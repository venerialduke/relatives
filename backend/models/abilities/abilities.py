# abilities.py
from models.abilities.base import Ability
from typing import Optional, Tuple
from utils.location_management import space_distance, are_adjacent_spaces
import uuid 
from models.entities.entity_content import get_structure_class_by_type


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
		resource_cost = kwargs.get("resource_cost", {})
		current_space = game_state.get_space_by_id(actor.location_space_id)

		if not structure_type:
			return "No structure type specified."

		if not current_space:
			return "Invalid space."

		if len(current_space.structures) >= current_space.max_buildings:
			return "Cannot build — building slot full."

		for res, amt in resource_cost.items():
			if actor.inventory.get(res, 0) < amt:
				return f"Insufficient resources: need {res} x{amt}"

		actor.update_inventory({k: -v for k, v in resource_cost.items()})

		cls = get_structure_class_by_type(structure_type)
		if not cls:
			return f"Unknown structure type: {structure_type}"

		structure_id = f"b_{uuid.uuid4().hex[:6]}"
		structure = cls(id=structure_id, location_space_id=current_space.id)

		current_space.structures.append(structure)
		game_state.structures[structure.id] = structure

		return f"Built {structure_type} on space {current_space.id}."

class MoveAbility(Ability):
	def __init__(self, max_distance=1, body_jump_cost=5, same_body_cost=1, resource_name="Fuel"):
		super().__init__("move", "moves the entity")
		self.max_distance = max_distance
		self.body_jump_cost = body_jump_cost
		self.same_body_cost = same_body_cost
		self.resource_name = resource_name

	def evaluate_move(self, entity, from_space, to_space) -> Tuple[bool, Optional[int], Optional[str]]:
		"""
		Returns: (can_move: bool, cost: int or None, error: str or None)
		"""
		if from_space.body_id == to_space.body_id:
			distance = space_distance(from_space, to_space)
			if distance > self.max_distance:
				return False, None, "Target too far"
			cost = self.same_body_cost * distance
		else:
			cost = self.body_jump_cost

		# If the entity has no inventory, treat move as free
		if not hasattr(entity, "inventory"):
			return True, 0, None

		available = entity.inventory.get(self.resource_name, 0)
		if available < cost:
			return False, cost, f"Not enough {self.resource_name}"

		return True, cost, None

	def execute_move(self, entity, from_space, to_space) -> Optional[str]:
		can_move, cost, error = self.evaluate_move(entity, from_space, to_space)
		if not can_move:
			return error

		if cost and hasattr(entity, "update_inventory"):
			entity.update_inventory({self.resource_name: -cost})

		entity.location_space_id = to_space.id
		if hasattr(entity, "mark_explored"):
			entity.mark_explored(to_space.id)

		return None  # success
