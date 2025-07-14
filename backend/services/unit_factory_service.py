"""
Unit Factory Service - handles autonomous unit construction and management.
"""

from typing import Dict, Any, Optional, List
from core.game_state import GameState
from models.entities.mining_drone import MiningDrone
from models.entities.structure_map import Factory
from models.entities.entities import AutonomousUnit
from config.game_config import FUEL_ID
import uuid


class UnitFactoryService:
    """Service for managing autonomous unit construction and lifecycle."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.unit_build_costs = {
            "mining_drone": {
                "iron": 10,
                "fuel": 5
            }
        }
        self.unit_build_time = {
            "mining_drone": 1  # Turns to build (currently instant after resource check)
        }
    
    def get_unit_build_costs(self, unit_type: str) -> Dict[str, Any]:
        """
        Get the resource costs for building a specific unit type.
        
        Args:
            unit_type: The type of unit to check costs for
            
        Returns:
            Dict with cost information or error
        """
        if unit_type not in self.unit_build_costs:
            return {
                "error": f"Unknown unit type: {unit_type}",
                "available_types": list(self.unit_build_costs.keys())
            }
        
        costs = self.unit_build_costs[unit_type]
        
        # Convert resource IDs to names for display
        named_costs = {}
        for resource_id, amount in costs.items():
            resource = self.game_state.get_resource_by_id(resource_id)
            if resource:
                named_costs[resource.name] = amount
            else:
                named_costs[resource_id] = amount  # Fallback to ID if resource not found
        
        return {
            "unit_type": unit_type,
            "costs": costs,
            "named_costs": named_costs,
            "build_time": self.unit_build_time.get(unit_type, 1)
        }
    
    def get_available_unit_types(self, factory_id: str = None) -> List[str]:
        """
        Get list of unit types that can be built.
        
        Args:
            factory_id: Optional factory ID to check specific factory capabilities
            
        Returns:
            List of available unit types
        """
        if factory_id:
            factory = self.game_state.get_structure_by_id(factory_id)
            if factory and hasattr(factory, 'supported_unit_types'):
                return factory.supported_unit_types
        
        # Return all available unit types
        return list(self.unit_build_costs.keys())
    
    def validate_unit_construction(self, factory_id: str, unit_type: str) -> Dict[str, Any]:
        """
        Validate whether a unit can be constructed at the specified factory.
        
        Args:
            factory_id: ID of the factory attempting to build
            unit_type: Type of unit to build
            
        Returns:
            Dict with validation result
        """
        # Check if factory exists
        factory = self.game_state.get_structure_by_id(factory_id)
        if not factory:
            return {
                "valid": False,
                "error": f"Factory {factory_id} not found"
            }
        
        # Check if factory is the right type
        if not isinstance(factory, Factory):
            return {
                "valid": False,
                "error": f"Structure {factory_id} is not a Factory"
            }
        
        # Check if factory can build this unit type
        if not factory.can_build_unit(unit_type):
            return {
                "valid": False,
                "error": f"Factory cannot build {unit_type}",
                "reasons": {
                    "on_cooldown": factory.build_cooldown > 0,
                    "unsupported_type": unit_type not in factory.supported_unit_types,
                    "cannot_build_this_turn": not factory.can_build_this_turn
                }
            }
        
        # Check resource requirements
        costs = self.unit_build_costs.get(unit_type, {})
        missing_resources = {}
        
        for resource_id, required_amount in costs.items():
            available = factory.inventory.get(resource_id, 0)
            if available < required_amount:
                missing_resources[resource_id] = required_amount - available
        
        if missing_resources:
            return {
                "valid": False,
                "error": "Insufficient resources",
                "missing_resources": missing_resources
            }
        
        return {
            "valid": True,
            "message": f"Can build {unit_type} at factory {factory_id}"
        }
    
    def build_mining_drone(self, factory_id: str, target_resource: str = "iron", 
                          drone_id: str = None) -> Dict[str, Any]:
        """
        Build a mining drone at the specified factory.
        
        Args:
            factory_id: ID of the factory to build at
            target_resource: Resource type for the drone to collect
            drone_id: Optional specific ID for the drone (generates one if None)
            
        Returns:
            Dict with build result
        """
        # Validate construction
        validation = self.validate_unit_construction(factory_id, "mining_drone")
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["error"],
                "details": validation.get("reasons", {})
            }
        
        # Get factory
        factory = self.game_state.get_structure_by_id(factory_id)
        
        # Generate ID if not provided
        if not drone_id:
            drone_id = f"mining_drone_{uuid.uuid4().hex[:8]}"
        
        # Get build costs
        build_costs = self.unit_build_costs["mining_drone"]
        
        # Use factory's build_unit method
        build_result = factory.build_unit("mining_drone", drone_id, build_costs, target_resource)
        
        if build_result["success"]:
            drone = build_result["unit"]
            
            # Add drone to game state (if game state has autonomous unit management)
            if hasattr(self.game_state, 'autonomous_units'):
                self.game_state.autonomous_units[drone_id] = drone
            elif hasattr(self.game_state, 'units'):
                self.game_state.units[drone_id] = drone
            
            return {
                "success": True,
                "message": f"Mining drone {drone_id} built successfully",
                "drone": drone.to_dict(self.game_state),
                "factory_status": {
                    "build_cooldown": factory.build_cooldown,
                    "can_build_this_turn": factory.can_build_this_turn,
                    "inventory": factory.inventory
                }
            }
        else:
            return {
                "success": False,
                "error": build_result["message"]
            }
    
    def get_factory_status(self, factory_id: str) -> Dict[str, Any]:
        """
        Get detailed status of a factory including build capabilities.
        
        Args:
            factory_id: ID of the factory to check
            
        Returns:
            Dict with factory status
        """
        factory = self.game_state.get_structure_by_id(factory_id)
        if not factory:
            return {
                "error": f"Factory {factory_id} not found"
            }
        
        if not isinstance(factory, Factory):
            return {
                "error": f"Structure {factory_id} is not a Factory"
            }
        
        # Get buildable units for this factory
        buildable_units = []
        for unit_type in factory.supported_unit_types:
            validation = self.validate_unit_construction(factory_id, unit_type)
            unit_info = {
                "unit_type": unit_type,
                "can_build": validation["valid"],
                "costs": self.unit_build_costs.get(unit_type, {}),
                "build_time": self.unit_build_time.get(unit_type, 1)
            }
            if not validation["valid"]:
                unit_info["build_error"] = validation["error"]
                unit_info["missing_resources"] = validation.get("missing_resources", {})
            
            buildable_units.append(unit_info)
        
        return {
            "factory_id": factory_id,
            "name": factory.name,
            "location": factory.location_space_id,
            "inventory": factory.inventory,
            "build_status": {
                "can_build_this_turn": factory.can_build_this_turn,
                "build_cooldown": factory.build_cooldown,
                "supported_unit_types": factory.supported_unit_types
            },
            "buildable_units": buildable_units,
            "is_collection_point": factory.is_collection_point()
        }
    
    def calculate_unit_maintenance_cost(self, unit_type: str, lifespan: int) -> Dict[str, int]:
        """
        Calculate ongoing maintenance costs for a unit over its lifespan.
        
        Args:
            unit_type: Type of unit
            lifespan: Expected lifespan in turns
            
        Returns:
            Dict of resource costs over lifespan
        """
        # For mining drones, fuel consumption is the main maintenance cost
        if unit_type == "mining_drone":
            fuel_per_turn = 1  # Approximate fuel usage per turn
            return {
                FUEL_ID: fuel_per_turn * lifespan
            }
        
        return {}
    
    def get_construction_summary(self, factory_id: str) -> Dict[str, Any]:
        """
        Get a summary of construction capabilities and current status.
        
        Args:
            factory_id: ID of the factory
            
        Returns:
            Summary dict with all relevant construction information
        """
        factory_status = self.get_factory_status(factory_id)
        
        if "error" in factory_status:
            return factory_status
        
        # Add overall summary information
        total_buildable = sum(1 for unit in factory_status["buildable_units"] if unit["can_build"])
        
        return {
            **factory_status,
            "summary": {
                "total_unit_types": len(factory_status["buildable_units"]),
                "currently_buildable": total_buildable,
                "ready_to_build": factory_status["build_status"]["can_build_this_turn"],
                "turns_until_ready": max(0, factory_status["build_status"]["build_cooldown"])
            }
        }