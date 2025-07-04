from dataclasses import dataclass, field
from typing import List, Optional
from abc import ABC, abstractmethod
from models.abilities.base import Ability
from models.entities.base import Actor  
from typing import List, Dict
from utils.resource_management import InventoryMixin

@dataclass
class Resource:
    id: str
    name: str
    properties: dict

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "properties": self.properties
        }

@dataclass
class Structure(Actor, InventoryMixin):
	id: str
	name: str
	location_space_id: str
	abilities: List[Ability] = field(default_factory=list)
	inventory: Dict[str, int] = field(default_factory=dict)
	explored_spaces: List[str] = field(default_factory=list)

	def to_dict(self):
		return {
			"id": self.id,
			"name": self.name,
			"location_space_id": self.location_space_id,
			"abilities": [ability.to_dict() for ability in self.abilities],
			"inventory": self.inventory,
			"explored_spaces":self.explored_spaces
		}

@dataclass
class Unit(Actor,InventoryMixin):
	id: str
	name: str
	location_space_id: str
	inventory: Dict[str, int] = field(default_factory=dict)
	health: int = 100
	damage: int = 0
	abilities: List[Ability] = field(default_factory=list)
	explored_spaces: List[str] = field(default_factory=list)

	def to_dict(self):
		return {
			"id": self.id,
			"name": self.name,
			"location_space_id": self.location_space_id,
			"inventory": self.inventory,
			"fuel": self.fuel,
			"health": self.health,
			"damage": self.damage,
			"abilities": [ability.to_dict() for ability in self.abilities],
			"explored_spaces":self.explored_spaces
		}