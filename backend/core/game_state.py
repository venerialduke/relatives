"""
Core game state management.
Centralized registry for all game objects without circular dependencies.
"""

from typing import Dict, List, Optional, Tuple, Any, TYPE_CHECKING
from config.game_config import HEX_DIRECTIONS

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from models.containers.containers import System, Body, Space
    from models.entities.entities import Unit, Structure, Resource
    from models.gameowners.owners import Player, SystemManager

class GameState:
    """
    Centralized game state manager.
    
    This class maintains all game objects and provides methods for accessing
    and querying them. It's designed to be the single source of truth for
    the current game state.
    """
    
    def __init__(self):
        # Core game object registries
        self.systems: Dict[str, 'System'] = {}
        self.bodies: Dict[str, 'Body'] = {}
        self.spaces: Dict[str, 'Space'] = {}
        self.units: Dict[str, 'Unit'] = {}
        self.players: Dict[str, 'Player'] = {}
        self.structures: Dict[str, 'Structure'] = {}
        self.resources: Dict[str, 'Resource'] = {}
        
        # Special accessibility tracking
        self.system_wide_accessible_spaces: List[str] = []  # Always accessible spaces

    # Basic entity getters
    def get_space_by_id(self, space_id: str) -> Optional['Space']:
        """Get space by ID."""
        return self.spaces.get(space_id)

    def get_body_by_id(self, body_id: str) -> Optional['Body']:
        """Get body by ID."""
        return self.bodies.get(body_id)

    def get_unit_by_id(self, unit_id: str) -> Optional['Unit']:
        """Get unit by ID."""
        return self.units.get(unit_id)

    def get_structure_by_id(self, structure_id: str) -> Optional['Structure']:
        """Get structure by ID."""
        return self.structures.get(structure_id)
    
    def get_player_by_id(self, player_id: str) -> Optional['Player']:
        """Get player by ID."""
        return self.players.get(player_id)

    def get_resource_by_id(self, resource_id: str) -> Optional['Resource']:
        """Get resource by ID."""
        return self.resources.get(resource_id)

    def get_system_by_id(self, system_id: str) -> Optional['System']:
        """Get system by ID."""
        return self.systems.get(system_id)

    # Resource management
    def find_resource_by_name(self, resource_name: str) -> Optional[str]:
        """Find resource ID by resource name."""
        for resource_id, resource in self.resources.items():
            if resource.name == resource_name:
                return resource_id
        return None

    # Spatial queries
    def get_spaces_in_radius(self, body: 'Body', center_location: Tuple[int, int], radius: int) -> List['Space']:
        """Get all spaces within a given radius of a center point."""
        cx, cy = center_location
        return [
            space for space in body.spaces
            if abs(space.q - cx) + abs(space.r - cy) <= radius
        ]

    def get_target_space_from_direction(self, current_space_id: str, direction: int) -> Optional['Space']:
        """Get the target space when moving in a specific direction."""
        origin = self.get_space_by_id(current_space_id)
        if not origin:
            return None
        
        dq, dr = HEX_DIRECTIONS[direction]
        target_q = origin.body_rel_q + dq
        target_r = origin.body_rel_r + dr

        body = self.get_body_by_id(origin.body_id)
        if not body:
            return None

        # Find space with matching relative coordinates
        return next(
            (space for space in body.spaces 
             if space.body_rel_q == target_q and space.body_rel_r == target_r),
            None
        )

    # Accessibility management
    def add_system_wide_accessible_space(self, space_id: str):
        """Add a space that's accessible to all players system-wide."""
        if space_id not in self.system_wide_accessible_spaces:
            self.system_wide_accessible_spaces.append(space_id)
    
    def get_all_accessible_spaces_for_unit(self, unit: 'Unit') -> List[str]:
        """Get all spaces accessible to a unit (unit-explored + system-wide)."""
        accessible_spaces = set(self.system_wide_accessible_spaces)
        if hasattr(unit, 'explored_spaces'):
            accessible_spaces.update(unit.explored_spaces)
        return list(accessible_spaces)

    # Serialization
    def to_dict(self) -> Dict[str, Any]:
        """Convert game state to dictionary for API responses."""
        return {
            "systems": {sid: system.to_dict() for sid, system in self.systems.items()},
            "bodies": {bid: body.to_dict() for bid, body in self.bodies.items()},
            "spaces": {sid: space.to_dict() for sid, space in self.spaces.items()},
            "units": {uid: unit.to_dict() for uid, unit in self.units.items()},
            "players": {pid: player.to_dict() for pid, player in self.players.items()},
            "structures": {sid: structure.to_dict() for sid, structure in self.structures.items()},
            "resources": {rid: resource.to_dict() for rid, resource in self.resources.items()},
            "system_wide_accessible_spaces": self.system_wide_accessible_spaces
        }

    # Advanced queries (for future optimization)
    def get_spaces_by_body(self, body_id: str) -> List['Space']:
        """Get all spaces belonging to a specific body."""
        return [space for space in self.spaces.values() if space.body_id == body_id]

    def get_units_by_player(self, player_id: str) -> List['Unit']:
        """Get all units owned by a specific player."""
        player = self.get_player_by_id(player_id)
        if not player:
            return []
        return [entity for entity in player.entities if hasattr(entity, 'location_space_id')]

    def get_structures_by_space(self, space_id: str) -> List['Structure']:
        """Get all structures in a specific space."""
        return [structure for structure in self.structures.values() 
                if structure.location_space_id == space_id]