"""
Movement service for handling unit movement operations.
"""

from typing import Optional, Dict, Any
from core.game_state import GameState
from models.entities.entity_content import PlayerUnit
from models.gameowners.owners import Player
from exceptions.game_exceptions import (
    MovementException, InsufficientFuelException, 
    InvalidLocationException, EntityNotFoundException
)
from config.game_config import HEX_DIRECTIONS, FUEL_ID
from utils.entity_utils import generate_space_id

class MovementService:
    """Service for handling all movement-related operations."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
    
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

        # Perform the actual move
        result = player.perform_unit_ability(
            actor_id=unit.id,
            game_state=self.game_state,
            ability="move",
            space_id=destination.id
        )

        if result:  # If there's an error message
            raise MovementException(result)

        return {
            "success": True,
            "unit": unit.to_dict(),
            "new_location": destination.to_dict(game_state=self.game_state)
        }
    
    def _handle_direct_movement(self, unit: PlayerUnit, current_space, target_space_id: str):
        """Handle direct movement to a specific space (inter-body)."""
        destination = self.game_state.get_space_by_id(target_space_id)
        if not destination:
            raise InvalidLocationException("Target space not found")
        
        # Check if unit has enough fuel for inter-body travel
        current_fuel = unit.inventory.get(FUEL_ID, 0)
        if current_fuel < 5:  # Inter-body movement cost
            raise InsufficientFuelException("Insufficient fuel for inter-body movement")
        
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
        
        # Check fuel for local movement
        current_fuel = unit.inventory.get(FUEL_ID, 0)
        if current_fuel < 1:  # Local movement cost
            raise InsufficientFuelException("Insufficient fuel for movement")
        
        return destination