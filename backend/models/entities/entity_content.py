from models.entities.entities import Structure,Unit
from models.abilities.abilities import BuildAbility,MoveAbility,CollectAbility

FUEL_ID = 'fuel'

class PlayerUnit(Unit):
    def __init__(self, id: str, location_space_id: str):
        super().__init__(
            id=id,
            name="Explorer",  # Or let this be dynamic if you want to pass it in
            location_space_id=location_space_id,
            abilities=[
                MoveAbility(max_distance=10, body_jump_cost=5, same_body_cost=1, resource_id=FUEL_ID),
                CollectAbility(),
                BuildAbility()
            ]
        )

    def advance_time(self, game_state):
        self.update_inventory({FUEL_ID: 1})