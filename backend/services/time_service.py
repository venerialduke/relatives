"""
Time service for handling game time advancement.
"""

from typing import Dict, Any
from core.game_state import GameState

class TimeService:
    """Service for handling time advancement and turn management."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.time_tick = 0
    
    def advance_time(self) -> Dict[str, Any]:
        """
        Advance game time by one tick and update all entities.
        
        Returns:
            Dict containing the new time state and updated entities
        """
        self.time_tick += 1

        # Advance time for all game entities in dependency order
        self._advance_units()
        self._advance_structures()
        self._advance_spaces()
        self._advance_bodies()
        self._advance_systems()

        return {
            "time": self.time_tick,
            "units": [unit.to_dict() for unit in self.game_state.units.values()],
            "structures": [structure.to_dict() for structure in self.game_state.structures.values()],
            "systems": [system.to_dict() for system in self.game_state.systems.values()]
        }
    
    def _advance_units(self):
        """Advance time for all units."""
        for unit in self.game_state.units.values():
            try:
                unit.advance_time(self.game_state)
            except Exception as e:
                print(f"Error advancing time for unit {unit.id}: {e}")
    
    def _advance_structures(self):
        """Advance time for all structures."""
        for structure in self.game_state.structures.values():
            try:
                structure.advance_time(self.game_state)
            except Exception as e:
                print(f"Error advancing time for structure {structure.id}: {e}")
    
    def _advance_spaces(self):
        """Advance time for all spaces."""
        for space in self.game_state.spaces.values():
            try:
                space.advance_time(self.game_state)
            except Exception as e:
                print(f"Error advancing time for space {space.id}: {e}")
    
    def _advance_bodies(self):
        """Advance time for all bodies."""
        for body in self.game_state.bodies.values():
            try:
                body.advance_time(self.game_state)
            except Exception as e:
                print(f"Error advancing time for body {body.id}: {e}")
    
    def _advance_systems(self):
        """Advance time for all systems."""
        for system in self.game_state.systems.values():
            try:
                system.advance_time(self.game_state)
            except Exception as e:
                print(f"Error advancing time for system {system.id}: {e}")
    
    def get_current_time(self) -> int:
        """Get the current game time tick."""
        return self.time_tick
    
    def set_time(self, new_time: int):
        """Set the game time (for loading saved games)."""
        self.time_tick = max(0, new_time)