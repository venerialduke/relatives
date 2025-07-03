# gameowner/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional,Tuple
from containers.containers import System, Body, Space 
from entities.entities import Unit, Structure, Resource 


class GameState:
    def __init__(self):
        self.systems: Dict[int, System] = {}
        self.bodies: Dict[int, Body] = {}
        self.spaces: Dict[int, Space] = {}
        self.units: Dict[int, Unit] = {}
        self.structures: Dict[int, Structure] = {}

    def get_space_by_id(self, space_id: int) -> Optional[Space]:
        return self.spaces.get(space_id)

    def get_body_by_id(self, body_id: int) -> Optional[Body]:
        return self.bodies.get(body_id)

    def get_unit_by_id(self, unit_id: int) -> Optional[Unit]:
        return self.units.get(unit_id)

    def get_structure_by_id(self, structure_id: int) -> Optional[Structure]:
        return self.structures.get(structure_id)

    def get_spaces_in_radius(self, body: Body, center_location: Tuple[int, int], radius: int) -> List[Space]:
        cx, cy = center_location
        return [
            space for space in body.spaces
            if abs(space.location[0] - cx) + abs(space.location[1] - cy) <= radius
        ]
