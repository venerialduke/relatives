"""
Mining Drone implementation - autonomous unit for resource collection.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List
from models.entities.entities import AutonomousUnit
from models.abilities.abilities import MoveAbility, CollectAbility
from config.game_config import FUEL_ID
from utils.location_management import space_distance


@dataclass
class MiningDrone(AutonomousUnit):
    """
    Autonomous mining drone that searches for resources, collects them,
    and deposits them at collection structures.
    """
    cargo_capacity: int = 10  # Maximum resources that can be carried
    target_resource: str = "iron"  # Primary resource to collect
    home_collection_point: Optional[str] = None  # ID of home collection structure
    
    def __init__(self, id: str, location_space_id: str, target_resource: str = "iron", 
                 home_collection_point: str = None, lifespan: int = 30, cargo_capacity: int = 10):
        super().__init__(
            id=id,
            name="Mining Drone",
            location_space_id=location_space_id,
            lifespan=lifespan,
            state="search",
            inventory={FUEL_ID: 10},  # Start with some fuel
            health=50,
            abilities=[
                MoveAbility(max_distance=10, same_body_cost=1, resource_id=FUEL_ID),
                CollectAbility()
            ]
        )
        self.cargo_capacity = cargo_capacity
        self.target_resource = target_resource
        self.home_collection_point = home_collection_point
        self.state_data = {
            "target_location": None,
            "turns_in_state": 0,
            "resource_locations": [],  # Cache of known resource locations
            "collection_points": []    # Cache of known collection points
        }
    
    def execute_state_logic(self, game_state):
        """
        Execute AI behavior based on current state.
        States: 'search', 'collect', 'deposit', 'returning'
        """
        self.state_data["turns_in_state"] += 1
        
        if self.state == "search":
            self._handle_search_state(game_state)
        elif self.state == "collect":
            self._handle_collect_state(game_state)
        elif self.state == "deposit":
            self._handle_deposit_state(game_state)
        elif self.state == "returning":
            self._handle_returning_state(game_state)
    
    def _handle_search_state(self, game_state):
        """
        Search for resources to collect. Transition to collect state when found.
        """
        current_space = game_state.get_space_by_id(self.location_space_id)
        if not current_space:
            return
        
        # Check if current space has target resource
        if self._space_has_target_resource(current_space):
            self.change_state("collect", {"target_location": current_space.id, "turns_in_state": 0})
            return
        
        # Look for nearby resources
        target_location = self._find_nearest_resource_location(game_state, current_space)
        
        if target_location:
            # Move towards resource location
            self._move_towards_target(game_state, target_location)
            if current_space.id == target_location:
                self.change_state("collect", {"target_location": target_location, "turns_in_state": 0})
        else:
            # No resources found, wander randomly
            self._wander_randomly(game_state)
    
    def _handle_collect_state(self, game_state):
        """
        Collect resources at current location. Transition when cargo full or no more resources.
        """
        current_space = game_state.get_space_by_id(self.location_space_id)
        if not current_space:
            return
        
        # Check if we're at capacity or space has no more resources
        current_cargo = sum(self.inventory.get(res, 0) for res in self.inventory if res != FUEL_ID)
        
        if current_cargo >= self.cargo_capacity:
            self.change_state("deposit", {"turns_in_state": 0})
            return
        
        if not self._space_has_target_resource(current_space):
            self.change_state("search", {"turns_in_state": 0})
            return
        
        # Collect resource
        self._collect_resource(game_state, current_space)
    
    def _handle_deposit_state(self, game_state):
        """
        Move to collection point and deposit cargo.
        """
        current_space = game_state.get_space_by_id(self.location_space_id)
        if not current_space:
            return
        
        # Find nearest collection point
        collection_point = self._find_nearest_collection_point(game_state, current_space)
        
        if not collection_point:
            # No collection point found, transition to returning home
            self.change_state("returning", {"turns_in_state": 0})
            return
        
        if current_space.id == collection_point:
            # At collection point, deposit cargo
            self._deposit_cargo(game_state, current_space)
            self.change_state("search", {"turns_in_state": 0})
        else:
            # Move towards collection point
            self._move_towards_target(game_state, collection_point)
    
    def _handle_returning_state(self, game_state):
        """
        Return to home collection point or wander if none set.
        """
        if self.home_collection_point:
            current_space = game_state.get_space_by_id(self.location_space_id)
            if current_space and current_space.id != self.home_collection_point:
                self._move_towards_target(game_state, self.home_collection_point)
            else:
                self.change_state("search", {"turns_in_state": 0})
        else:
            self.change_state("search", {"turns_in_state": 0})
    
    def _space_has_target_resource(self, space) -> bool:
        """Check if space has the target resource available."""
        return space.inventory.get(self.target_resource, 0) > 0
    
    def _find_nearest_resource_location(self, game_state, current_space) -> Optional[str]:
        """Find the nearest space with target resource."""
        current_body = game_state.get_body_by_id(current_space.body_id)
        if not current_body:
            return None
        
        nearest_space = None
        min_distance = float('inf')
        
        for space in current_body.spaces:
            if self._space_has_target_resource(space):
                distance = space_distance(current_space, space)
                if distance < min_distance:
                    min_distance = distance
                    nearest_space = space.id
        
        return nearest_space
    
    def _find_nearest_collection_point(self, game_state, current_space) -> Optional[str]:
        """Find the nearest collection structure."""
        current_body = game_state.get_body_by_id(current_space.body_id)
        if not current_body:
            return None
        
        nearest_space = None
        min_distance = float('inf')
        
        for space in current_body.spaces:
            # Check if space has collection structures
            for structure in space.structures:
                if hasattr(structure, 'is_collection_point') and structure.is_collection_point():
                    distance = space_distance(current_space, space)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_space = space.id
                        break
        
        return nearest_space
    
    def _move_towards_target(self, game_state, target_space_id: str):
        """Move one step towards target space."""
        current_space = game_state.get_space_by_id(self.location_space_id)
        target_space = game_state.get_space_by_id(target_space_id)
        
        if not current_space or not target_space:
            return
        
        # Simple pathfinding - move in direction that reduces distance
        current_body = game_state.get_body_by_id(current_space.body_id)
        if not current_body:
            return
        
        best_move = None
        min_distance = space_distance(current_space, target_space)
        
        # Check adjacent spaces
        directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        for dq, dr in directions:
            new_q = current_space.body_rel_q + dq
            new_r = current_space.body_rel_r + dr
            
            # Check if this space exists
            from utils.entity_utils import generate_space_id
            potential_space_id = generate_space_id(current_body, new_q, new_r)
            potential_space = game_state.get_space_by_id(potential_space_id)
            
            if potential_space:
                distance = space_distance(potential_space, target_space)
                if distance < min_distance:
                    min_distance = distance
                    best_move = potential_space_id
        
        # Execute move if beneficial
        if best_move and self.inventory.get(FUEL_ID, 0) > 0:
            self.location_space_id = best_move
            self.inventory[FUEL_ID] -= 1
    
    def _wander_randomly(self, game_state):
        """Move randomly when no target is found."""
        import random
        
        current_space = game_state.get_space_by_id(self.location_space_id)
        current_body = game_state.get_body_by_id(current_space.body_id)
        
        if not current_space or not current_body:
            return
        
        # Random direction
        directions = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        dq, dr = random.choice(directions)
        
        new_q = current_space.body_rel_q + dq
        new_r = current_space.body_rel_r + dr
        
        from utils.entity_utils import generate_space_id
        potential_space_id = generate_space_id(current_body, new_q, new_r)
        potential_space = game_state.get_space_by_id(potential_space_id)
        
        if potential_space and self.inventory.get(FUEL_ID, 0) > 0:
            self.location_space_id = potential_space_id
            self.inventory[FUEL_ID] -= 1
    
    def _collect_resource(self, game_state, space):
        """Collect target resource from current space."""
        available = space.inventory.get(self.target_resource, 0)
        if available > 0:
            # Collect 1 unit per turn
            space.inventory[self.target_resource] -= 1
            self.inventory[self.target_resource] = self.inventory.get(self.target_resource, 0) + 1
    
    def _deposit_cargo(self, game_state, space):
        """Deposit all cargo at collection structure."""
        # Find collection structure on this space
        collection_structure = None
        for structure in space.structures:
            if hasattr(structure, 'is_collection_point') and structure.is_collection_point():
                collection_structure = structure
                break
        
        if not collection_structure:
            return
        
        # Transfer all non-fuel resources to structure
        for resource_id, amount in list(self.inventory.items()):
            if resource_id != FUEL_ID and amount > 0:
                collection_structure.inventory[resource_id] = collection_structure.inventory.get(resource_id, 0) + amount
                self.inventory[resource_id] = 0
    
    def to_dict(self, game_state=None):
        """Convert to dictionary with mining drone specific fields."""
        data = super().to_dict(game_state)
        data.update({
            "cargo_capacity": self.cargo_capacity,
            "target_resource": self.target_resource,
            "home_collection_point": self.home_collection_point,
            "unit_type": "mining_drone"
        })
        return data