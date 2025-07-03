# gameowner/player.py

from gameowner.base import GameOwner

class Player(GameOwner):
    def __init__(self, name: str, description: str = "", player_id: str = ""):
        super().__init__(name, description)
        self.player_id = player_id  # External reference (auth, socket ID, etc.)

    def perform(self, actor_id, game_state, **kwargs):
        # Example: issue a command to one of your units
        actor = game_state.get_unit_by_id(actor_id)
        if actor.id not in self.units:
            return "Permission denied"
        
        ability_name = kwargs.get("ability")
        for ability in actor.abilities:
            if ability.name == ability_name:
                return ability.perform(actor, game_state, **kwargs)

        return "Ability not found"

class SystemManager(GameOwner):
    def __init__(self, system_id: int, name: str = "System", description: str = ""):
        super().__init__(name, description)
        self.system_id = system_id  # Which system this manager governs

    def perform(self, actor_id, game_state, **kwargs):
        # Could control autonomous NPCs, buildings, events, etc.
        actor = game_state.get_unit_by_id(actor_id)
        if actor.id not in self.units:
            return "System does not control this unit"

        ability_name = kwargs.get("ability")
        for ability in actor.abilities:
            if ability.name == ability_name:
                return ability.perform(actor, game_state, **kwargs)

        return "Ability not found"