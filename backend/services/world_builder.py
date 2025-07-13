"""
World generation service.
Handles creation and initialization of game worlds.
"""

import random
import uuid
from typing import List, Tuple

from core.game_state import GameState
from models.containers.containers import System, Body, Space
from models.entities.entities import Resource
from models.entities.entity_content import PlayerUnit
from models.gameowners.owners import Player
from utils.location_management import estimate_body_radius
from utils.entity_utils import generate_space_id, get_starting_inventory
from config.game_config import (
    RESOURCE_NAMES, FUEL_ID, BODY_DEFINITIONS, HEX_DIRECTIONS,
    WORLD_GENERATION, GAME_BALANCE
)

class WorldBuilder:
    """Service for generating game worlds and initializing game state."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
    
    def generate_resource_pool(self, resource_names: List[str]) -> List[Resource]:
        """Generate the resource pool and register resources in game state."""
        resource_list = []
        
        for idx, name in enumerate(resource_names):
            resource = Resource(
                id=f"res_{idx+1}",
                name=name,
                properties={}
            )
            resource_list.append(resource)
            self.game_state.resources[resource.id] = resource
        
        # Add fuel resource
        fuel_resource = Resource(id=FUEL_ID, name='Fuel', properties={})
        resource_list.append(fuel_resource)
        self.game_state.resources[FUEL_ID] = fuel_resource
        
        return resource_list
    
    def create_player(self, player_id: str, name: str) -> Player:
        """Create and register a new player."""
        player = Player(name=name, description="The human player", player_id=player_id)
        self.game_state.players[player.player_id] = player
        return player
    
    def create_player_unit(self, unit_id: str, player: Player) -> PlayerUnit:
        """Create and register a player unit with starting inventory."""
        player_unit = PlayerUnit(id=unit_id, location_space_id=None)
        player_unit.update_inventory(get_starting_inventory(self.game_state))
        
        player.entities.append(player_unit)  # Mark ownership
        self.game_state.units[player_unit.id] = player_unit
        
        return player_unit
    
    def generate_system(
        self, 
        system_name: str, 
        player_unit: PlayerUnit, 
        resource_pool: List[Resource], 
        body_definitions: List[Tuple[str, int]]
    ) -> System:
        """Generate a complete star system with bodies and spaces."""
        
        # Create the system
        system = System(
            id=str(uuid.uuid4()),
            name=system_name,
            q=0,
            r=0
        )
        self.game_state.systems[system.id] = system
        
        # Generate bodies within the system
        used_coords = set()
        radius_between_bodies = WORLD_GENERATION["radius_between_bodies"]
        max_attempts = WORLD_GENERATION["max_placement_attempts"]
        
        def is_area_free(center_q: int, center_r: int, radius: int) -> bool:
            """Check if an area is free for body placement."""
            for dq in range(-radius, radius + 1):
                for dr in range(max(-radius, -dq - radius), min(radius, -dq + radius) + 1):
                    q, r = center_q + dq, center_r + dr
                    if (q, r) in used_coords:
                        return False
            return True

        def mark_area_used(center_q: int, center_r: int, radius: int):
            """Mark an area as used for body placement."""
            for dq in range(-radius, radius + 1):
                for dr in range(max(-radius, -dq - radius), min(radius, -dq + radius) + 1):
                    q, r = center_q + dq, center_r + dr
                    used_coords.add((q, r))

        def find_open_coord(required_radius: int) -> Tuple[int, int]:
            """Find an open coordinate for body placement."""
            # Spiral out to find usable open body anchor
            for radius in range(1, max_attempts):
                q, r = 0, -radius
                for direction in range(6):
                    for _ in range(radius):
                        dq, dr = HEX_DIRECTIONS[direction]
                        cand_q = q + random.choice([-1, 0, 1])
                        cand_r = r + random.choice([-1, 0, 1])
                        cand_q *= (required_radius + radius_between_bodies)
                        cand_r *= (required_radius + radius_between_bodies)
                        
                        if is_area_free(cand_q, cand_r, required_radius + radius_between_bodies):
                            mark_area_used(cand_q, cand_r, required_radius)
                            return (cand_q, cand_r)
                        q += dq
                        r += dr
            
            raise Exception("Failed to find non-overlapping body location")

        # Generate each body
        for body_index, (body_name, space_count) in enumerate(body_definitions):
            body_radius = estimate_body_radius(space_count)
            body_q, body_r = find_open_coord(body_radius)

            body = Body(
                id=f"body_{body_index + 1}",
                system_id=system.id,
                name=body_name,
                q=body_q,
                r=body_r,
            )
            self.game_state.bodies[body.id] = body

            # Generate spaces for this body
            for i in range(space_count):
                next_q, next_r = body.get_next_space_coords()
                space_id = generate_space_id(body, next_q, next_r)
                
                space = Space(
                    id=space_id,
                    body_rel_q=next_q,
                    body_rel_r=next_r,
                    name=f"{body.name} - Space {i+1}",
                    body_id=body.id,
                    inventory={},
                )
                space.set_global_coords(body.q, body.r)

                # Populate space with random resources
                resource_count_range = WORLD_GENERATION["resource_count_range"]
                num_resources = random.randint(*resource_count_range)
                selected_resources = random.sample(resource_pool, min(num_resources, len(resource_pool)))
                
                for resource in selected_resources:
                    space.inventory[resource.id] = space.inventory.get(resource.id, 0) + 1

                body.add_space(space)
                self.game_state.spaces[space.id] = space
                
                # Make the first space of each body system-wide accessible
                if i == 0:  # First space (center space)
                    self.game_state.add_system_wide_accessible_space(space.id)
                    
                    # Add a Space Port to the first space of each body for testing
                    self._create_space_port_at_space(space_id, body_index)

            system.bodies.append(body)

        # Place player unit at first space of first body
        if system.bodies and system.bodies[0].spaces:
            player_unit.location_space_id = system.bodies[0].spaces[0].id
        else:
            raise ValueError("No spaces created; can't place unit.")

        return system
    
    def build_default_world(self) -> Tuple[System, Player, PlayerUnit]:
        """Build the default game world with all standard components."""
        
        # Generate resources
        resource_pool = self.generate_resource_pool(RESOURCE_NAMES)
        
        # Create player
        player = self.create_player('player_1', "Player 1")
        
        # Create player unit
        player_unit = self.create_player_unit("u1", player)
        
        # Generate the star system
        system = self.generate_system(
            system_name="Eos System",
            player_unit=player_unit,
            resource_pool=resource_pool,
            body_definitions=BODY_DEFINITIONS
        )
        
        return system, player, player_unit
    
    def _create_space_port_at_space(self, space_id: str, body_index: int):
        """Create a Space Port at the specified space for testing purposes."""
        from models.entities.structures.space_port import SpacePort
        import uuid
        
        space_port = SpacePort(
            id=f"test_port_{body_index + 1}",
            location_space_id=space_id
        )
        
        # Register the Space Port in game state
        self.game_state.structures[space_port.id] = space_port
        
        # Add the Space Port to the space's structures list
        space = self.game_state.get_space_by_id(space_id)
        if space:
            space.structures.append(space_port)