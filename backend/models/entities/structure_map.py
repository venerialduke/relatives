from models.entities.entities import Structure
from models.entities.structures.space_port import SpacePort
from models.entities.traits import CollectionStructure

class Collector(Structure):
    def __init__(self, id: str, location_space_id: str):
        super().__init__(id=id, name="Collector", location_space_id=location_space_id)

class Factory(Structure, CollectionStructure):
    def __init__(self, id: str, location_space_id: str):
        super().__init__(id=id, name="Factory", location_space_id=location_space_id)
        self.can_build_this_turn = True
        self.build_cooldown = 0
        self.supported_unit_types = ["mining_drone"]  # Units this factory can build
    
    def can_build_unit(self, unit_type: str) -> bool:
        """Check if this factory can build the specified unit type."""
        return (self.can_build_this_turn and 
                self.build_cooldown <= 0 and 
                unit_type in self.supported_unit_types)
    
    def build_unit(self, unit_type: str, unit_id: str, build_costs: dict, target_resource: str = "iron") -> dict:
        """
        Build a unit at this factory location.
        
        Args:
            unit_type: Type of unit to build (e.g., "mining_drone")
            unit_id: Unique ID for the new unit
            build_costs: Dict of resource_id -> amount required
            target_resource: Target resource for mining units
            
        Returns:
            Dict with build result
        """
        if not self.can_build_unit(unit_type):
            return {
                "success": False,
                "message": f"Cannot build {unit_type} - factory not ready or unsupported type"
            }
        
        # Check if factory has required resources
        missing_resources = {}
        for resource_id, required_amount in build_costs.items():
            available = self.inventory.get(resource_id, 0)
            if available < required_amount:
                missing_resources[resource_id] = required_amount - available
        
        if missing_resources:
            return {
                "success": False,
                "message": "Insufficient resources for unit construction",
                "missing_resources": missing_resources
            }
        
        # Consume resources
        for resource_id, cost in build_costs.items():
            self.inventory[resource_id] -= cost
        
        # Create the unit based on type
        if unit_type == "mining_drone":
            from models.entities.mining_drone import MiningDrone
            new_unit = MiningDrone(
                id=unit_id,
                location_space_id=self.location_space_id,
                target_resource=target_resource,
                home_collection_point=self.id
            )
        else:
            return {
                "success": False,
                "message": f"Unknown unit type: {unit_type}"
            }
        
        # Set build cooldown
        self.can_build_this_turn = False
        self.build_cooldown = 3  # Can't build for 3 turns
        
        return {
            "success": True,
            "message": f"Successfully built {unit_type}",
            "unit": new_unit,
            "cooldown_turns": self.build_cooldown
        }
    
    def advance_time(self, game_state):
        """Handle factory time advancement including build cooldowns."""
        super().advance_time(game_state)
        
        # Reduce build cooldown
        if self.build_cooldown > 0:
            self.build_cooldown -= 1
            if self.build_cooldown <= 0:
                self.can_build_this_turn = True
    
    def to_dict(self, game_state=None):
        """Enhanced factory serialization with build status."""
        data = super().to_dict(game_state)
        data.update({
            "can_build_this_turn": self.can_build_this_turn,
            "build_cooldown": self.build_cooldown,
            "supported_unit_types": self.supported_unit_types,
            "structure_type": "Factory"
        })
        return data

class Settlement(Structure):
    def __init__(self, id: str, location_space_id: str):
        super().__init__(id=id, name="Settlement", location_space_id=location_space_id)

class FuelPump(Structure):
    def __init__(self, id: str, location_space_id: str):
        super().__init__(id=id, name="Fuel Pump", location_space_id=location_space_id)
    
    def advance_time(self, game_state):
        # Generate 1 fuel per turn
        FUEL_ID = 'fuel'
        self.update_inventory({FUEL_ID: 1})
        super().advance_time(game_state)

class Scanner(Structure):
    def __init__(self, id: str, location_space_id: str):
        super().__init__(id=id, name="Scanner", location_space_id=location_space_id)


STRUCTURE_CLS_MAP = {
    "Collector": Collector,
    "Factory": Factory,
    "Settlement": Settlement,
    "FuelPump": FuelPump,
    "Scanner": Scanner,
    "SpacePort": SpacePort
}

def get_structure_class_by_type(type_name: str):
    return STRUCTURE_CLS_MAP.get(type_name)