# abilities.py
from abilities.base import Ability

class CollectAbility(Ability):
    def __init__(self):
        super().__init__("collect", "Collects resources from the current space.")

    def perform(self, actor, game_state, **kwargs):
        space = game_state.get_space_by_id(actor.location_space_id)
        if not space or not space.resource_ids:
            return "Nothing to collect."
        collected = []
        while space.resource_ids and len(actor.inventory_resource_ids) < 5:
            resource_id = space.resource_ids.pop()
            actor.inventory_resource_ids.append(resource_id)
            collected.append(resource_id)
        return f"Collected: {collected}"


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
        if len(target_space.unit_ids) >= target_space.max_units:
            return "Target space full."

        robot.location_space_id = target_space_id
        target_space.unit_ids.append(robot.id)
        return f"Deployed {robot.name} to space {target_space_id}."


class BuildAbility(Ability):
    def __init__(self):
        super().__init__("build", "Constructs a structure on this space using resources.")

    def perform(self, actor, game_state, **kwargs):
        structure_type = kwargs.get("structure_type")
        current_space = game_state.get_space_by_id(actor.location_space_id)

        if len(current_space.building_ids) >= current_space.max_buildings:
            return "Cannot build — building slot full."

        # You can check resource requirements here
        structure = game_state.build_structure(structure_type, location_space_id=current_space.id)
        current_space.building_ids.append(structure.id)
        return f"Built {structure_type} on space {current_space.id}."
