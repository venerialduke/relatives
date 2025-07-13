"""
Utility functions for entity management and queries.
Extracted from app.py for better organization.
"""

from typing import Optional, List, Dict, Any
from core.game_state import GameState
from models.entities.entities import Unit
from models.entities.entity_content import PlayerUnit
from utils.resource_management import get_named_inventory
from config.game_config import FUEL_ID, get_starting_inventory_requirements

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

def get_movement_options_for_unit(game_state: GameState, unit_id: str) -> Dict[str, Any]:
    """Get all available movement options for a unit."""
    unit = game_state.get_unit_by_id(unit_id)
    if not unit:
        return {"error": "Unit not found"}
    
    current_fuel = unit.inventory.get(FUEL_ID, 0)
    current_space = game_state.get_space_by_id(unit.location_space_id)
    
    if not current_space:
        return {"error": "Current space not found"}
    
    # Get all bodies except current one
    current_body_id = current_space.body_id
    reachable_bodies = []
    
    for body in game_state.bodies.values():
        if body.id == current_body_id:
            continue  # Skip current body
            
        # Get explored spaces on this body (unit-explored + system-wide accessible)
        explored_spaces = []
        accessible_space_ids = game_state.get_all_accessible_spaces_for_unit(unit)
        
        for space in body.spaces:
            if space.id in accessible_space_ids:
                explored_spaces.append({
                    "space_id": space.id,
                    "name": space.name,
                    "q": space.q,
                    "r": space.r,
                    "named_inventory": get_named_inventory(space.inventory, game_state)
                })
        
        # Only include bodies with explored spaces
        if explored_spaces:
            reachable_bodies.append({
                "body_id": body.id,
                "name": body.name,
                "fuel_cost": 5,  # Inter-body movement cost
                "explored_spaces": explored_spaces
            })
    
    return {
        "reachable_bodies": reachable_bodies,
        "current_fuel": current_fuel,
        "inter_body_cost": 5
    }