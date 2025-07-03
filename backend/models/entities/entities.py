from dataclasses import dataclass, field
from typing import List, Optional
from abc import ABC, abstractmethod
from abilities import Ability
from entities.base import Actor  

@dataclass
class Resource:
    id: int
    name: str
    properties: dict

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "properties": self.properties
        }

@dataclass
class Structure(Actor):
    id: int
    name: str
    location_space_id: int
    abilities: List[Ability] = field(default_factory=list)
    inventory_resource_ids: List[int] = field(default_factory=list)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location_space_id": self.location_space_id,
            "abilities": [ability.to_dict() for ability in self.abilities],
            "inventory_resource_ids": self.inventory_resource_ids
        }

@dataclass
class Unit(Actor):
    id: int
    name: str
    location_space_id: int
    inventory_resource_ids: List[int] = field(default_factory=list)
    fuel: int = 0
    health: int = 100
    damage: int = 0
    abilities: List[Ability] = field(default_factory=list)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location_space_id": self.location_space_id,
            "inventory_resource_ids": self.inventory_resource_ids,
            "fuel": self.fuel,
            "health": self.health,
            "damage": self.damage,
            "abilities": [ability.to_dict() for ability in self.abilities]
        }