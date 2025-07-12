# gameowner/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional,Tuple
from models.containers.containers import System, Body, Space 
from models.entities.entities import Unit, Structure, Resource 
from models.gameowners.owners import Player,SystemManager

HEX_DIRECTIONS = [
    (1, 0),   # 0 - E
    (1, -1),  # 1 - NE
    (0, -1),  # 2 - NW
    (-1, 0),  # 3 - W
    (-1, 1),  # 4 - SW
    (0, 1)    # 5 - SE
]

class GameState:
    def __init__(self):
        self.systems: Dict[str, System] = {}
        self.bodies: Dict[str, Body] = {}
        self.spaces: Dict[str, Space] = {}
        self.units: Dict[str, Unit] = {}
        self.players: Dict[str,Player] = {}
        self.structures: Dict[str, Structure] = {}
        self.resources: Dict[str, Resource] = {}
        

    def get_space_by_id(self, space_id: str) -> Optional[Space]:
        return self.spaces.get(space_id)

    def get_body_by_id(self, body_id: str) -> Optional[Body]:
        return self.bodies.get(body_id)

    def get_unit_by_id(self, unit_id: str) -> Optional[Unit]:
        return self.units.get(unit_id)

    def get_structure_by_id(self, structure_id: str) -> Optional[Structure]:
        return self.structures.get(structure_id)
    
    def get_player_by_id(self, player_id: str) -> Optional[Player]:
        return self.players.get(player_id)

    def get_spaces_in_radius(self, body: Body, center_location: Tuple[int, int], radius: int) -> List[Space]:
        cx, cy = center_location
        return [
            space for space in body.spaces
            if abs(space.location[0] - cx) + abs(space.location[1] - cy) <= radius
        ]

    def get_resource_by_id(self, resource_id: str) -> Optional[Resource]:
        return self.resources.get(resource_id)

    def get_target_space_from_direction(self, current_space_id: str, direction: int) -> Optional[Space]:
        origin = self.get_space_by_id(current_space_id)
        if not origin:
            return None
        
        dq, dr = HEX_DIRECTIONS[direction]
        target_q = origin.q + dq
        target_r = origin.r + dr

        body = self.get_body_by_id(origin.body_id)
        if not body:
            return None

        return next(
            (space for space in body.spaces if space.q == target_q and space.r == target_r),
            None
        )
