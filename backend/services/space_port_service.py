"""
Space Port service for network operations.
Simple implementation following existing service patterns.
"""

from typing import List, Dict, Optional
from core.game_state import GameState
from models.entities.structures.space_port import SpacePort
from config.game_config import SPACE_PORT_TRAVEL_COST, FUEL_ID

class SpacePortService:
    """Simple service for Space Port network operations."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
    
    def get_all_space_ports(self) -> List[SpacePort]:
        """Get all Space Port structures."""
        return [
            structure for structure in self.game_state.structures.values()
            if isinstance(structure, SpacePort)
        ]
    
    def get_accessible_space_ports(self, unit) -> List[SpacePort]:
        """Get Space Ports accessible to a unit."""
        accessible_spaces = self.game_state.get_all_accessible_spaces_for_unit(unit)
        return [
            port for port in self.get_all_space_ports()
            if port.location_space_id in accessible_spaces and port.is_operational
        ]
    
    def find_space_port_at_space(self, space_id: str) -> Optional[SpacePort]:
        """Find Space Port at a specific space."""
        for port in self.get_all_space_ports():
            if port.location_space_id == space_id:
                return port
        return None
    
    def get_space_port_destinations(self, from_space_id: str, unit) -> List[Dict]:
        """Get available Space Port destinations from current location."""
        origin_port = self.find_space_port_at_space(from_space_id)
        if not origin_port or not origin_port.is_operational:
            return []
        
        destinations = []
        accessible_ports = self.get_accessible_space_ports(unit)
        
        for dest_port in accessible_ports:
            if dest_port.id != origin_port.id and origin_port.can_connect_to(dest_port):
                dest_space = self.game_state.get_space_by_id(dest_port.location_space_id)
                dest_body = self.game_state.get_body_by_id(dest_space.body_id) if dest_space else None
                
                destinations.append({
                    "space_id": dest_port.location_space_id,
                    "space_name": dest_space.name if dest_space else "Unknown",
                    "body_name": dest_body.name if dest_body else "Unknown", 
                    "fuel_cost": SPACE_PORT_TRAVEL_COST,
                    "travel_type": "space_port"
                })
        
        return destinations
    
    def validate_space_port_travel(self, unit, from_space_id: str, to_space_id: str) -> tuple[bool, str]:
        """Validate Space Port travel between two spaces."""
        # Check origin
        origin_port = self.find_space_port_at_space(from_space_id)
        if not origin_port or not origin_port.is_operational:
            return False, "No operational Space Port at origin"
        
        # Check destination  
        dest_port = self.find_space_port_at_space(to_space_id)
        if not dest_port or not dest_port.is_operational:
            return False, "No operational Space Port at destination"
        
        # Check accessibility
        accessible_ports = self.get_accessible_space_ports(unit)
        if dest_port not in accessible_ports:
            return False, "Destination Space Port not accessible"
        
        # Check fuel
        current_fuel = unit.inventory.get(FUEL_ID, 0)
        if current_fuel < SPACE_PORT_TRAVEL_COST:
            return False, f"Insufficient fuel (need {SPACE_PORT_TRAVEL_COST}, have {current_fuel})"
        
        return True, "Space Port travel valid"
    
    def is_space_port_travel(self, from_space_id: str, to_space_id: str) -> bool:
        """Check if movement between spaces is Space Port travel."""
        origin_port = self.find_space_port_at_space(from_space_id)
        dest_port = self.find_space_port_at_space(to_space_id)
        
        return (
            origin_port is not None and origin_port.is_operational and
            dest_port is not None and dest_port.is_operational and
            origin_port.can_connect_to(dest_port)
        )