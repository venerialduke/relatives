"""
Collection service for handling resource collection operations.
"""

from typing import Optional, Dict, Any
from core.game_state import GameState
from models.entities.entity_content import PlayerUnit
from models.gameowners.owners import Player
from exceptions.game_exceptions import (
    CollectionException, InsufficientResourcesException,
    EntityNotFoundException, InvalidLocationException
)
from utils.entity_utils import find_resource_id_by_name

class CollectionService:
    """Service for handling all resource collection operations."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
    
    def collect_resource(
        self,
        player: Player,
        unit_id: str,
        resource_input: str,
        quantity: Optional[int] = None,
        space_id: Optional[str] = None,
        structure_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Collect resources from a space or structure.
        
        Args:
            player: The player performing the collection
            unit_id: ID of the unit collecting
            resource_input: Resource name or ID to collect
            quantity: Amount to collect (optional, defaults to all available)
            space_id: Space to collect from (optional, defaults to unit's location)
            structure_id: Structure to collect from (optional)
            
        Returns:
            Dict containing collection result
            
        Raises:
            CollectionException: For various collection failures
        """
        
        # Validate unit
        unit = self._validate_unit(player, unit_id)
        
        # Determine collection location
        space = self._determine_collection_space(unit, space_id)
        
        # Resolve resource ID
        resource_id = self._resolve_resource_id(resource_input)
        
        # Perform collection based on source
        if structure_id:
            return self._collect_from_structure(unit, resource_id, resource_input, quantity, structure_id, space)
        else:
            return self._collect_from_space(player, unit, resource_id, resource_input, quantity, space)
    
    def _validate_unit(self, player: Player, unit_id: str) -> PlayerUnit:
        """Validate that the unit exists and is owned by the player."""
        unit = self.game_state.get_unit_by_id(unit_id)
        if not unit:
            raise EntityNotFoundException(f"Unit {unit_id} not found")
        
        if not player.owns_actor(unit):
            raise CollectionException(f"Player does not own unit {unit_id}")
        
        return unit
    
    def _determine_collection_space(self, unit: PlayerUnit, space_id: Optional[str]):
        """Determine which space to collect from."""
        if space_id:
            space = self.game_state.get_space_by_id(space_id)
            if not space:
                raise InvalidLocationException(f"Space {space_id} not found")
        else:
            space = self.game_state.get_space_by_id(unit.location_space_id)
            if not space:
                raise InvalidLocationException("Unit's current space not found")
        
        return space
    
    def _resolve_resource_id(self, resource_input: str) -> str:
        """Convert resource name to ID if needed."""
        resource_id = find_resource_id_by_name(self.game_state, resource_input)
        if not resource_id:
            # Maybe it's already an ID, try using it directly
            resource_id = resource_input
            # Validate it exists
            if not self.game_state.get_resource_by_id(resource_id):
                raise CollectionException(f"Unknown resource: {resource_input}")
        
        return resource_id
    
    def _collect_from_structure(
        self, 
        unit: PlayerUnit, 
        resource_id: str, 
        resource_input: str, 
        quantity: Optional[int], 
        structure_id: str,
        space
    ) -> Dict[str, Any]:
        """Handle collection from a structure."""
        structure = self.game_state.get_structure_by_id(structure_id)
        if not structure:
            raise EntityNotFoundException(f"Structure {structure_id} not found")
        
        available = structure.inventory.get(resource_id, 0)
        if available <= 0:
            raise InsufficientResourcesException(
                f"No {resource_input} available in structure"
            )

        take = min(quantity or available, available)
        structure.update_inventory({resource_id: -take})
        unit.update_inventory({resource_id: take})
        
        result_message = f"Collected {take} x {resource_input} from {structure.name}."
        
        return {
            "result": result_message,
            "unit": unit.to_dict(game_state=self.game_state),
            "space": space.to_dict(game_state=self.game_state),
            "structure": structure.to_dict(game_state=self.game_state)
        }
    
    def _collect_from_space(
        self, 
        player: Player, 
        unit: PlayerUnit, 
        resource_id: str, 
        resource_input: str, 
        quantity: Optional[int],
        space
    ) -> Dict[str, Any]:
        """Handle collection from a space using the ability system."""
        result = player.perform_unit_ability(
            actor_id=unit.id,
            game_state=self.game_state,
            ability="collect",
            resource_id=resource_id,
            quantity=quantity
        )
        
        if isinstance(result, str) and ("cannot" in result.lower() or "insufficient" in result.lower()):
            raise CollectionException(result)

        return {
            "result": result,
            "unit": unit.to_dict(game_state=self.game_state),
            "space": space.to_dict(game_state=self.game_state)
        }