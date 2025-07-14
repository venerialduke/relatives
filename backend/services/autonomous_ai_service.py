"""
Autonomous AI Service - manages AI behavior for autonomous units.
"""

from typing import Dict, Any, List, Optional
from core.game_state import GameState
from models.entities.entities import AutonomousUnit
from models.entities.mining_drone import MiningDrone
from models.entities.traits import CollectionStructure
from utils.location_management import space_distance


class AutonomousAIService:
    """Service for managing autonomous unit AI behavior and processing."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.ai_processors = {
            "mining_drone": self.execute_mining_drone_ai
        }
    
    def process_autonomous_units(self) -> Dict[str, Any]:
        """
        Process all autonomous units for one turn.
        
        Returns:
            Dict with processing results and statistics
        """
        processed_units = 0
        expired_units = []
        state_changes = {}
        errors = []
        
        # Get all autonomous units from game state
        autonomous_units = self.get_autonomous_units()
        
        for unit_id, unit in autonomous_units.items():
            try:
                # Process the unit
                result = self.process_single_unit(unit)
                
                if result["expired"]:
                    expired_units.append(unit_id)
                
                if result["state_changed"]:
                    state_changes[unit_id] = {
                        "old_state": result["old_state"],
                        "new_state": result["new_state"]
                    }
                
                processed_units += 1
                
            except Exception as e:
                errors.append({
                    "unit_id": unit_id,
                    "error": str(e)
                })
        
        # Remove expired units from game state
        for unit_id in expired_units:
            self.remove_expired_unit(unit_id)
        
        return {
            "processed_units": processed_units,
            "expired_units": expired_units,
            "state_changes": state_changes,
            "errors": errors,
            "total_autonomous_units": len(autonomous_units)
        }
    
    def process_single_unit(self, unit: AutonomousUnit) -> Dict[str, Any]:
        """
        Process a single autonomous unit for one turn.
        
        Args:
            unit: The autonomous unit to process
            
        Returns:
            Dict with processing result
        """
        old_state = unit.state
        old_lifespan = unit.lifespan
        
        # Call the unit's advance_time method
        unit.advance_time(self.game_state)
        
        return {
            "unit_id": unit.id,
            "old_state": old_state,
            "new_state": unit.state,
            "state_changed": old_state != unit.state,
            "lifespan_changed": old_lifespan != unit.lifespan,
            "expired": unit.state == "expired" or unit.lifespan <= 0
        }
    
    def execute_mining_drone_ai(self, drone: MiningDrone) -> Dict[str, Any]:
        """
        Execute AI logic specifically for mining drones.
        
        Args:
            drone: The mining drone to process
            
        Returns:
            Dict with AI execution result
        """
        old_state = drone.state
        
        # The drone's own execute_state_logic handles the AI
        # This method can add additional logging/monitoring
        actions_taken = []
        
        # Check if drone is near resources
        current_space = self.game_state.get_space_by_id(drone.location_space_id)
        if current_space:
            # Log resource availability
            resources_available = {k: v for k, v in current_space.inventory.items() if v > 0}
            if resources_available:
                actions_taken.append(f"Found resources: {resources_available}")
        
        # Check if drone is near collection points
        collection_points = self.find_nearby_collection_points(drone.location_space_id)
        if collection_points:
            actions_taken.append(f"Near collection points: {len(collection_points)}")
        
        return {
            "drone_id": drone.id,
            "old_state": old_state,
            "new_state": drone.state,
            "actions_taken": actions_taken,
            "cargo_load": sum(drone.inventory.get(res, 0) for res in drone.inventory if res != "fuel"),
            "fuel_remaining": drone.inventory.get("fuel", 0)
        }
    
    def find_nearest_collection_point(self, space_id: str, max_distance: int = 20) -> Optional[str]:
        """
        Find the nearest collection structure to a given space.
        
        Args:
            space_id: The space to search from
            max_distance: Maximum search distance
            
        Returns:
            Space ID of nearest collection point, or None
        """
        current_space = self.game_state.get_space_by_id(space_id)
        if not current_space:
            return None
        
        current_body = self.game_state.get_body_by_id(current_space.body_id)
        if not current_body:
            return None
        
        nearest_space = None
        min_distance = float('inf')
        
        for space in current_body.spaces:
            # Check if space has collection structures
            for structure in space.structures:
                if hasattr(structure, 'is_collection_point') and structure.is_collection_point():
                    distance = space_distance(current_space, space)
                    if distance < min_distance and distance <= max_distance:
                        min_distance = distance
                        nearest_space = space.id
                        break
        
        return nearest_space
    
    def find_nearby_collection_points(self, space_id: str, radius: int = 10) -> List[Dict[str, Any]]:
        """
        Find all collection points within a radius of a space.
        
        Args:
            space_id: The space to search from
            radius: Search radius
            
        Returns:
            List of collection point information
        """
        current_space = self.game_state.get_space_by_id(space_id)
        if not current_space:
            return []
        
        current_body = self.game_state.get_body_by_id(current_space.body_id)
        if not current_body:
            return []
        
        collection_points = []
        
        for space in current_body.spaces:
            distance = space_distance(current_space, space)
            if distance <= radius:
                for structure in space.structures:
                    if hasattr(structure, 'is_collection_point') and structure.is_collection_point():
                        collection_points.append({
                            "space_id": space.id,
                            "structure_id": structure.id,
                            "structure_name": structure.name,
                            "distance": distance,
                            "inventory": structure.inventory.copy()
                        })
        
        # Sort by distance
        collection_points.sort(key=lambda x: x["distance"])
        return collection_points
    
    def find_best_resource_location(self, space_id: str, resource_type: str, 
                                  max_distance: int = 15) -> Optional[Dict[str, Any]]:
        """
        Find the best resource location for collection.
        
        Args:
            space_id: The space to search from
            resource_type: Type of resource to find
            max_distance: Maximum search distance
            
        Returns:
            Dict with best resource location info, or None
        """
        current_space = self.game_state.get_space_by_id(space_id)
        if not current_space:
            return None
        
        current_body = self.game_state.get_body_by_id(current_space.body_id)
        if not current_body:
            return None
        
        best_location = None
        best_score = -1
        
        for space in current_body.spaces:
            resource_amount = space.inventory.get(resource_type, 0)
            if resource_amount > 0:
                distance = space_distance(current_space, space)
                if distance <= max_distance:
                    # Score based on resource amount and proximity
                    score = resource_amount / (distance + 1)  # +1 to avoid division by zero
                    
                    if score > best_score:
                        best_score = score
                        best_location = {
                            "space_id": space.id,
                            "distance": distance,
                            "resource_amount": resource_amount,
                            "score": score
                        }
        
        return best_location
    
    def get_autonomous_units(self) -> Dict[str, AutonomousUnit]:
        """
        Get all autonomous units from the game state.
        
        Returns:
            Dict of unit_id -> AutonomousUnit
        """
        autonomous_units = {}
        
        # Check if game state has dedicated autonomous units collection
        if hasattr(self.game_state, 'autonomous_units'):
            return self.game_state.autonomous_units
        
        # Otherwise, search through regular units
        if hasattr(self.game_state, 'units'):
            for unit_id, unit in self.game_state.units.items():
                if isinstance(unit, AutonomousUnit):
                    autonomous_units[unit_id] = unit
        
        return autonomous_units
    
    def remove_expired_unit(self, unit_id: str):
        """
        Remove an expired unit from the game state.
        
        Args:
            unit_id: ID of the unit to remove
        """
        # Remove from autonomous units if present
        if hasattr(self.game_state, 'autonomous_units') and unit_id in self.game_state.autonomous_units:
            del self.game_state.autonomous_units[unit_id]
        
        # Remove from regular units if present
        if hasattr(self.game_state, 'units') and unit_id in self.game_state.units:
            del self.game_state.units[unit_id]
    
    def get_unit_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about autonomous units.
        
        Returns:
            Dict with statistics
        """
        autonomous_units = self.get_autonomous_units()
        
        stats = {
            "total_units": len(autonomous_units),
            "by_type": {},
            "by_state": {},
            "average_lifespan": 0,
            "low_fuel_units": [],
            "near_expiration_units": []
        }
        
        total_lifespan = 0
        
        for unit_id, unit in autonomous_units.items():
            # Count by type
            unit_type = getattr(unit, 'unit_type', type(unit).__name__)
            stats["by_type"][unit_type] = stats["by_type"].get(unit_type, 0) + 1
            
            # Count by state
            stats["by_state"][unit.state] = stats["by_state"].get(unit.state, 0) + 1
            
            # Track lifespan
            total_lifespan += unit.lifespan
            
            # Check for low fuel (if applicable)
            fuel_amount = unit.inventory.get("fuel", 0)
            if fuel_amount < 3:
                stats["low_fuel_units"].append({
                    "unit_id": unit_id,
                    "fuel": fuel_amount,
                    "location": unit.location_space_id
                })
            
            # Check for near expiration
            if unit.lifespan <= 5:
                stats["near_expiration_units"].append({
                    "unit_id": unit_id,
                    "lifespan": unit.lifespan,
                    "state": unit.state
                })
        
        if len(autonomous_units) > 0:
            stats["average_lifespan"] = total_lifespan / len(autonomous_units)
        
        return stats
    
    def force_unit_state_change(self, unit_id: str, new_state: str, 
                              state_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Manually change a unit's state (for debugging/admin purposes).
        
        Args:
            unit_id: ID of the unit to modify
            new_state: New state to set
            state_data: Optional state data to set
            
        Returns:
            Dict with operation result
        """
        autonomous_units = self.get_autonomous_units()
        
        if unit_id not in autonomous_units:
            return {
                "success": False,
                "error": f"Unit {unit_id} not found"
            }
        
        unit = autonomous_units[unit_id]
        old_state = unit.state
        
        unit.change_state(new_state, state_data or {})
        
        return {
            "success": True,
            "unit_id": unit_id,
            "old_state": old_state,
            "new_state": new_state,
            "state_data": unit.state_data
        }