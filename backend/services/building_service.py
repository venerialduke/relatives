"""
Building service for handling structure construction operations.
"""

from typing import Dict, Any
from core.game_state import GameState
from models.entities.entity_content import PlayerUnit
from models.gameowners.owners import Player
from exceptions.game_exceptions import (
    BuildingException, InvalidStructureTypeException,
    EntityNotFoundException, InsufficientResourcesException
)
from models.entities.structure_map import get_structure_class_by_type
from config.game_config import STRUCTURE_REQUIREMENTS

class BuildingService:
    """Service for handling all building construction operations."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
    
    def build_structure(
        self,
        player: Player,
        unit_id: str,
        structure_type: str
    ) -> Dict[str, Any]:
        """
        Build a structure at the unit's current location.
        
        Args:
            player: The player performing the build
            unit_id: ID of the unit building
            structure_type: Type of structure to build (e.g., "Factory", "Collector")
            
        Returns:
            Dict containing build result
            
        Raises:
            BuildingException: For various building failures
        """
        
        # Validate unit
        unit = self._validate_unit(player, unit_id)
        
        # Validate structure type and get requirements
        resource_cost_names = self._validate_structure_type(structure_type)
        
        # Get structure class
        structure_cls = get_structure_class_by_type(structure_type)
        if not structure_cls:
            raise InvalidStructureTypeException(
                f"No class found for structure: {structure_type}"
            )
        
        # Convert resource names to IDs for BuildAbility
        resource_cost = self._convert_resource_requirements(resource_cost_names)
        
        # Perform the build using the unit's BuildAbility
        result = player.perform_unit_ability(
            actor_id=unit.id,
            game_state=self.game_state,
            ability="build",
            structure_type=structure_type,
            resource_cost=resource_cost
        )
        
        # Handle structured result or error message
        if isinstance(result, str) and (
            result.startswith("Cannot build") or 
            result.startswith("Insufficient") or
            "not enough" in result.lower()
        ):
            raise BuildingException(result)
        
        # Get updated space information
        space = self.game_state.get_space_by_id(unit.location_space_id)
        
        return {
            "result": result,
            "unit": unit.to_dict(game_state=self.game_state),
            "space": space.to_dict(game_state=self.game_state) if space else None
        }
    
    def _validate_unit(self, player: Player, unit_id: str) -> PlayerUnit:
        """Validate that the unit exists and is owned by the player."""
        unit = self.game_state.get_unit_by_id(unit_id)
        if not unit:
            raise EntityNotFoundException(f"Unit {unit_id} not found")
        
        if not player.owns_actor(unit):
            raise BuildingException(f"Player does not own unit {unit_id}")
        
        return unit
    
    def _validate_structure_type(self, structure_type: str) -> Dict[str, int]:
        """Validate structure type and return resource requirements."""
        resource_cost_names = STRUCTURE_REQUIREMENTS.get(structure_type)
        if not resource_cost_names:
            raise InvalidStructureTypeException(
                f"Unknown structure type: {structure_type}"
            )
        
        return resource_cost_names
    
    def _convert_resource_requirements(self, resource_cost_names: Dict[str, int]) -> Dict[str, int]:
        """Convert resource names to IDs for ability system."""
        resource_cost = {}
        for resource_name, quantity in resource_cost_names.items():
            resource_id = self.game_state.find_resource_by_name(resource_name)
            if resource_id:
                resource_cost[resource_id] = quantity
            else:
                raise BuildingException(f"Unknown resource required: {resource_name}")
        
        return resource_cost
    
    def get_building_requirements(self, structure_type: str) -> Dict[str, Any]:
        """Get the resource requirements for building a specific structure type."""
        try:
            resource_cost_names = self._validate_structure_type(structure_type)
            resource_cost = self._convert_resource_requirements(resource_cost_names)
            
            # Convert back to names for display
            requirements = {}
            for resource_id, quantity in resource_cost.items():
                resource = self.game_state.get_resource_by_id(resource_id)
                if resource:
                    requirements[resource.name] = quantity
            
            return {
                "structure_type": structure_type,
                "requirements": requirements,
                "total_cost": sum(resource_cost.values())
            }
        except (InvalidStructureTypeException, BuildingException) as e:
            return {"error": str(e)}
    
    def can_afford_structure(self, unit_id: str, structure_type: str) -> Dict[str, Any]:
        """Check if a unit can afford to build a specific structure."""
        unit = self.game_state.get_unit_by_id(unit_id)
        if not unit:
            return {"error": "Unit not found", "can_afford": False}
        
        try:
            resource_cost_names = self._validate_structure_type(structure_type)
            resource_cost = self._convert_resource_requirements(resource_cost_names)
            
            missing_resources = {}
            can_afford = True
            
            for resource_id, required_quantity in resource_cost.items():
                available = unit.inventory.get(resource_id, 0)
                if available < required_quantity:
                    can_afford = False
                    resource = self.game_state.get_resource_by_id(resource_id)
                    resource_name = resource.name if resource else resource_id
                    missing_resources[resource_name] = required_quantity - available
            
            return {
                "can_afford": can_afford,
                "missing_resources": missing_resources,
                "structure_type": structure_type
            }
        except (InvalidStructureTypeException, BuildingException) as e:
            return {"error": str(e), "can_afford": False}