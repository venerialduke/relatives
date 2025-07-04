from models.entities.entities import Structure,Unit
from models.abilities.abilities import BuildAbility,MoveAbility,CollectAbility

class Collector(Structure):
    def __init__(self, id: str, location_space_id: str):
        super().__init__(id=id, name="Collector", location_space_id=location_space_id)

class Factory(Structure):
    def __init__(self, id: str, location_space_id: str):
        super().__init__(id=id, name="Factory", location_space_id=location_space_id)

class Settlement(Structure):
    def __init__(self, id: str, location_space_id: str):
        super().__init__(id=id, name="Settlement", location_space_id=location_space_id)

class FuelPump(Structure):
    def __init__(self, id: str, location_space_id: str):
        super().__init__(id=id, name="Fuel Pump", location_space_id=location_space_id)

class Scanner(Structure):
    def __init__(self, id: str, location_space_id: str):
        super().__init__(id=id, name="Scanner", location_space_id=location_space_id)


STRUCTURE_CLS_MAP = {
    "Collector": Collector,
    "Factory": Factory,
    "Settlement": Settlement,
    "FuelPump": FuelPump,
    "Scanner": Scanner
}

def get_structure_class_by_type(type_name: str):
    return STRUCTURE_CLS_MAP.get(type_name)

class PlayerUnit(Unit):
    def __init__(self, id: str, location_space_id: str):
        super().__init__(
            id=id,
            name="Explorer",  # Or let this be dynamic if you want to pass it in
            location_space_id=location_space_id,
            inventory={"Fuel": 0},
            abilities=[
                MoveAbility(max_distance=1, body_jump_cost=5, same_body_cost=1, resource_name="Fuel"),
                CollectAbility(),
                BuildAbility()
            ]
        )

    def advance_time(self, game_state):
        self.update_inventory({"Fuel": 1})