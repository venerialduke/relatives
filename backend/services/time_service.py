"""
Time service for handling game time advancement.
"""

from typing import Dict, Any
from core.game_state import GameState
from services.autonomous_ai_service import AutonomousAIService

class TimeService:
    """Service for handling time advancement and turn management."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.time_tick = 0
        self.autonomous_ai_service = AutonomousAIService(game_state)
    
    def advance_time(self) -> Dict[str, Any]:
        """
        Advance game time by one tick and update all entities.
        
        Returns:
            Dict containing the new time state and updated entities
        """
        self.time_tick += 1

        # Process autonomous units first (they may affect other entities)
        autonomous_result = self._advance_autonomous_units()
        
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
            "systems": [system.to_dict() for system in self.game_state.systems.values()],
            "autonomous_units": autonomous_result
        }
    
    def _advance_units(self):
        """Advance time for all units."""
        for unit in self.game_state.units.values():
            try:
                unit.advance_time(self.game_state)
            except Exception as e:
                print(f"Error advancing time for unit {unit.id}: {e}")
    
    def _advance_autonomous_units(self) -> Dict[str, Any]:
        """Process autonomous units AI and lifecycle."""
        try:
            return self.autonomous_ai_service.process_autonomous_units()
        except Exception as e:
            print(f"Error processing autonomous units: {e}")
            return {
                "processed_units": 0,
                "expired_units": [],
                "state_changes": {},
                "errors": [{"error": str(e)}],
                "total_autonomous_units": 0
            }
    
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
    
    def get_autonomous_unit_statistics(self) -> Dict[str, Any]:
        """Get statistics about autonomous units."""
        return self.autonomous_ai_service.get_unit_statistics()
    
    def manage_factory_cooldowns(self):
        """Manage factory build cooldowns during time advancement."""
        from models.entities.structure_map import Factory
        
        for structure in self.game_state.structures.values():
            if isinstance(structure, Factory):
                # Factory cooldowns are handled in their advance_time method
                # This is just for additional logging/monitoring if needed
                pass
    
    def handle_unit_expiration(self, expired_units: list):
        """Handle cleanup when units expire."""
        for unit_id in expired_units:
            # Log expiration
            print(f"Unit {unit_id} has expired and been removed from game state")
            
            # Additional cleanup could be added here if needed
            # (e.g., dropping inventory, notifying other systems, etc.)
    
    def get_time_advancement_summary(self) -> Dict[str, Any]:
        """Get a summary of the last time advancement."""
        autonomous_stats = self.get_autonomous_unit_statistics()
        
        return {
            "current_time": self.time_tick,
            "autonomous_units": {
                "total": autonomous_stats["total_units"],
                "by_type": autonomous_stats["by_type"],
                "by_state": autonomous_stats["by_state"],
                "low_fuel_count": len(autonomous_stats["low_fuel_units"]),
                "near_expiration_count": len(autonomous_stats["near_expiration_units"])
            },
            "structures": {
                "total": len(self.game_state.structures) if hasattr(self.game_state, 'structures') else 0
            },
            "units": {
                "total": len(self.game_state.units) if hasattr(self.game_state, 'units') else 0
            }
        }