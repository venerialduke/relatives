"""
Space Port structure implementation.
Enables reduced-cost inter-body travel following existing structure patterns.
"""

from typing import Dict, Any, Optional
from models.entities.entities import Structure
from config.game_config import SPACE_PORT_TRAVEL_COST

class SpacePort(Structure):
    """
    Space Port structure enabling reduced-cost inter-body travel.
    Simple implementation following existing structure patterns.
    """
    
    def __init__(self, id: str, location_space_id: str):
        super().__init__(id=id, name="Space Port", location_space_id=location_space_id)
        self.is_operational = True
        self.structure_type = "SpacePort"
    
    def get_travel_cost(self) -> Optional[int]:
        """Get fuel cost for traveling to/from this Space Port."""
        return SPACE_PORT_TRAVEL_COST if self.is_operational else None
    
    def can_connect_to(self, other_port: 'SpacePort') -> bool:
        """Check if this Space Port can connect to another."""
        return self.is_operational and other_port.is_operational
    
    def to_dict(self, game_state=None) -> Dict[str, Any]:
        data = super().to_dict(game_state)
        data.update({
            "is_operational": self.is_operational,
            "travel_cost": self.get_travel_cost(),
            "structure_type": "SpacePort"
        })
        return data
    
    def advance_time(self, game_state):
        """Space Port time advancement."""
        super().advance_time(game_state)
        # Future: maintenance, operational status changes, etc.