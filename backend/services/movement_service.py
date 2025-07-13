"""
Movement service for handling unit movement operations.
"""

from typing import Optional, Dict, Any, Tuple
from core.game_state import GameState
from models.entities.entity_content import PlayerUnit
from models.gameowners.owners import Player
from exceptions.game_exceptions import (
    MovementException, InsufficientFuelException, 
    InvalidLocationException, EntityNotFoundException
)
from config.game_config import HEX_DIRECTIONS, FUEL_ID, SPACE_PORT_TRAVEL_COST, INTER_BODY_FUEL_COST
from utils.entity_utils import generate_space_id
from utils.location_management import space_distance
from services.space_port_service import SpacePortService

class MovementCalculator:
    """Unified movement cost calculation and validation."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.space_port_service = SpacePortService(game_state)
    
    def calculate_movement_cost(self, from_space, to_space) -> Tuple[int, str, str]:
        """
        Calculate movement cost and type for any movement.
        
        Returns:
            (cost: int, movement_type: str, description: str)
        """
        if from_space.body_id == to_space.body_id:
            # Same body movement
            distance = space_distance(from_space, to_space)
            return distance, "same_body", f"{distance} hex{'es' if distance != 1 else ''} distance"
        else:
            # Inter-body movement - check for space port
            if self.space_port_service.is_space_port_travel(from_space.id, to_space.id):
                return SPACE_PORT_TRAVEL_COST, "space_port", "Space Port Network travel"
            else:
                return INTER_BODY_FUEL_COST, "inter_body", "Standard inter-body travel"
    
    def validate_movement(self, unit: PlayerUnit, from_space, to_space) -> Tuple[bool, Optional[str]]:
        """
        Validate if movement is possible.
        
        Returns:
            (is_valid: bool, error_message: Optional[str])
        """
        cost, movement_type, _ = self.calculate_movement_cost(from_space, to_space)
        
        # Check fuel availability
        available_fuel = unit.inventory.get(FUEL_ID, 0)
        if available_fuel < cost:
            return False, f"Insufficient fuel (need {cost}, have {available_fuel})"
        
        # Check distance limit for same-body movement
        if movement_type == "same_body" and cost > 10:  # Max same-body distance
            return False, "Target too far"
        
        return True, None

class MovementService:
    """Service for handling all movement-related operations."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.calculator = MovementCalculator(game_state)
        self.space_port_service = SpacePortService(game_state)
    
    def move_unit(
        self, 
        player: Player,
        unit_id: str, 
        direction: Optional[int] = None, 
        target_space_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Move a unit either by direction or to a specific space.
        
        Args:
            player: The player performing the move
            unit_id: ID of the unit to move
            direction: Direction to move (0-5) for local movement
            target_space_id: Specific space ID for inter-body movement
            
        Returns:
            Dict containing move result or error information
            
        Raises:
            MovementException: For various movement failures
        """
        
        # Validate unit exists and is owned by player
        unit = self.game_state.get_unit_by_id(unit_id)
        if not unit or not isinstance(unit, PlayerUnit):
            raise EntityNotFoundException(f"Unit {unit_id} not found")
        
        if not player.owns_actor(unit):
            raise MovementException(f"Player does not own unit {unit_id}")
        
        current_space = self.game_state.get_space_by_id(unit.location_space_id)
        if not current_space:
            raise InvalidLocationException("Current space not found")

        # Determine destination space
        destination = None
        
        if target_space_id:
            # Direct space movement (inter-body)
            destination = self._handle_direct_movement(unit, current_space, target_space_id)
        elif direction is not None:
            # Directional movement (same body)
            destination = self._handle_directional_movement(unit, current_space, direction)
        else:
            raise MovementException("Must provide either direction or space_id")

        # Calculate movement cost using unified calculator
        cost, movement_type, description = self.calculator.calculate_movement_cost(current_space, destination)
        
        # Validate movement
        is_valid, error_msg = self.calculator.validate_movement(unit, current_space, destination)
        if not is_valid:
            raise MovementException(error_msg)
        
        # Perform the actual move with calculated cost
        kwargs = {
            "actor_id": unit.id,
            "game_state": self.game_state,
            "ability": "move",
            "space_id": destination.id,
            "fuel_cost": cost  # Always override with calculated cost
        }
            
        result = player.perform_unit_ability(**kwargs)

        if result:  # If there's an error message
            raise MovementException(result)

        return {
            "success": True,
            "unit": unit.to_dict(),
            "new_location": destination.to_dict(game_state=self.game_state)
        }
    
    def _handle_direct_movement(self, unit: PlayerUnit, current_space, target_space_id: str):
        """Handle direct movement to a specific space."""
        destination = self.game_state.get_space_by_id(target_space_id)
        if not destination:
            raise InvalidLocationException("Target space not found")
        
        return destination
    
    def _handle_directional_movement(self, unit: PlayerUnit, current_space, direction: int):
        """Handle directional movement within the same body."""
        # Validate direction
        if direction < 0 or direction >= len(HEX_DIRECTIONS):
            raise InvalidLocationException(f"Invalid direction: {direction}")
        
        # Update unit direction
        unit.direction = direction
        
        # Calculate destination coordinates
        dq, dr = HEX_DIRECTIONS[direction]
        dest_q = current_space.body_rel_q + dq
        dest_r = current_space.body_rel_r + dr

        # Find target space in same body
        body = self.game_state.get_body_by_id(current_space.body_id)
        if not body:
            raise InvalidLocationException("Current body not found")
        
        destination_id = generate_space_id(body, dest_q, dest_r)
        destination = self.game_state.get_space_by_id(destination_id)

        if not destination:
            raise InvalidLocationException("No space in that direction")
        
        return destination