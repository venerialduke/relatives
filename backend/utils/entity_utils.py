"""
Utility functions for entity management and queries.
Extracted from app.py for better organization.
"""

from typing import Optional, List, Dict, Any
from core.game_state import GameState
from models.entities.entities import Unit
from models.entities.entity_content import PlayerUnit
from utils.resource_management import get_named_inventory
from config.game_config import FUEL_ID, get_starting_inventory_requirements, SPACE_PORT_TRAVEL_COST, INTER_BODY_FUEL_COST

def find_resource_id_by_name(game_state: GameState, resource_name: str) -> Optional[str]:
    """
    Convert resource name to resource ID.
    Deprecated - use game_state.find_resource_by_name() directly.
    """
    return game_state.find_resource_by_name(resource_name)

def find_space(game_state: GameState, space_id: str):
    """Find space by ID."""
    return game_state.get_space_by_id(space_id)

def find_body_by_space(game_state: GameState, space_id: str):
    """Find the body containing a specific space."""
    space = game_state.get_space_by_id(space_id)
    if space and space.body_id:
        return game_state.get_body_by_id(space.body_id)
    return None

def find_unit(game_state: GameState, unit_id: Optional[str] = None, unit_name: Optional[str] = None) -> Optional[Unit]:
    """Find unit by ID or name."""
    if unit_id and unit_id in game_state.units:
        return game_state.units[unit_id]
    if unit_name:
        for u in game_state.units.values():
            if hasattr(u, 'name') and u.name.lower() == unit_name.lower():
                return u
    return None

def find_player_units(game_state: GameState, player_id: str) -> List[Dict[str, Any]]:
    """Get all units owned by a player."""
    results = []
    player = game_state.get_player_by_id(player_id)
    if not player:
        return results
    
    for entity in player.entities:
        if isinstance(entity, PlayerUnit):
            results.append(entity.to_dict(game_state=game_state))
    return results

def get_starting_inventory(game_state: GameState) -> Dict[str, int]:
    """Generate starting inventory with enough resources to build all structures."""
    required_resources = get_starting_inventory_requirements()
    
    # Convert resource names to IDs using game state
    starting_inventory = {}
    
    for resource_name, quantity in required_resources.items():
        if resource_name == FUEL_ID:
            # Fuel ID is already correct
            starting_inventory[FUEL_ID] = quantity
        else:
            resource_id = game_state.find_resource_by_name(resource_name)
            if resource_id:
                starting_inventory[resource_id] = quantity
    
    return starting_inventory

def generate_space_id(body, rel_q: int, rel_r: int) -> str:
    """Generate a unique space ID based on body and relative coordinates."""
    return f"body:{body.id}:{rel_q}:{rel_r}"

def get_movement_destinations_for_unit(game_state: GameState, unit_id: str) -> Dict[str, Any]:
    """Get all available movement destinations for a unit with unified cost calculation."""
    unit = game_state.get_unit_by_id(unit_id)
    if not unit:
        return {"error": "Unit not found"}
    
    current_fuel = unit.inventory.get(FUEL_ID, 0)
    current_space = game_state.get_space_by_id(unit.location_space_id)
    
    if not current_space:
        return {"error": "Current space not found"}
    
    # Import movement calculator (inside function to avoid circular imports)
    from services.movement_service import MovementCalculator
    calculator = MovementCalculator(game_state)
    
    destinations = []
    accessible_space_ids = game_state.get_all_accessible_spaces_for_unit(unit)
    
    # Check all accessible spaces (same body and other bodies)
    for space_id in accessible_space_ids:
        if space_id == current_space.id:
            continue  # Skip current location
            
        target_space = game_state.get_space_by_id(space_id)
        if not target_space:
            continue
            
        # Calculate movement cost and type
        cost, movement_type, description = calculator.calculate_movement_cost(current_space, target_space)
        
        # Determine travel icon
        icon = {
            "same_body": "🚶",
            "space_port": "🚀", 
            "inter_body": "🌍"
        }.get(movement_type, "🚶")
        
        # Get body name
        body = game_state.get_body_by_id(target_space.body_id)
        body_name = body.name if body else "Unknown Body"
        
        destinations.append({
            "space_id": target_space.id,
            "space_name": target_space.name,
            "body_name": body_name,
            "cost": cost,
            "movement_type": movement_type,
            "description": description,
            "icon": icon,
            "can_afford": current_fuel >= cost,
            "is_same_body": target_space.body_id == current_space.body_id
        })
    
    # Sort by cost, then by name
    destinations.sort(key=lambda d: (d["cost"], d["space_name"]))
    
    return {
        "destinations": destinations,
        "current_fuel": current_fuel,
        "current_space_id": current_space.id
    }

def calculate_movement_cost_for_unit(game_state: GameState, unit_id: str, target_space_id: str) -> Dict[str, Any]:
    """Calculate movement cost for a specific destination."""
    unit = game_state.get_unit_by_id(unit_id)
    if not unit:
        return {"error": "Unit not found"}
    
    current_space = game_state.get_space_by_id(unit.location_space_id)
    target_space = game_state.get_space_by_id(target_space_id)
    
    if not current_space:
        return {"error": "Current space not found"}
    if not target_space:
        return {"error": "Target space not found"}
    
    # Import movement calculator (inside function to avoid circular imports)
    from services.movement_service import MovementCalculator
    calculator = MovementCalculator(game_state)
    
    cost, movement_type, description = calculator.calculate_movement_cost(current_space, target_space)
    is_valid, error_msg = calculator.validate_movement(unit, current_space, target_space)
    
    current_fuel = unit.inventory.get(FUEL_ID, 0)
    
    # Determine travel icon
    icon = {
        "same_body": "🚶",
        "space_port": "🚀", 
        "inter_body": "🌍"
    }.get(movement_type, "🚶")
    
    # Get body name
    body = game_state.get_body_by_id(target_space.body_id)
    body_name = body.name if body else "Unknown Body"
    
    return {
        "cost": cost,
        "movement_type": movement_type,
        "description": description,
        "icon": icon,
        "body_name": body_name,
        "can_afford": current_fuel >= cost,
        "is_valid": is_valid,
        "error": error_msg,
        "current_fuel": current_fuel,
        "remaining_fuel": current_fuel - cost if is_valid else current_fuel
    }