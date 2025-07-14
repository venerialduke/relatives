from dataclasses import dataclass, field
from typing import List, Optional
from abc import ABC, abstractmethod
from models.abilities.base import Ability
from models.entities.base import Actor  
from typing import List, Dict
from utils.resource_management import InventoryMixin, get_named_inventory
from config.game_config import FUEL_ID

from enum import IntEnum

class HexDirection(IntEnum):
    E = 0       # (1, 0)
    NE = 1      # (1, -1)
    NW = 2      # (0, -1)
    W = 3       # (-1, 0)
    SW = 4      # (-1, 1)
    SE = 5      # (0, 1)

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
	direction: int = HexDirection.E

	def to_dict(self, game_state=None):
		data = {
			"id": self.id,
			"name": self.name,
			"location_space_id": self.location_space_id,
			"direction": self.direction,
			"abilities": [ability.to_dict() for ability in self.abilities],
			"inventory": self.inventory,
			"explored_spaces":self.explored_spaces
		}

		if game_state:
			data["named_inventory"] = get_named_inventory(self.inventory, game_state)

		return data

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
	direction: int = HexDirection.E

	def to_dict(self, game_state=None):
		data = {
			"id": self.id,
			"name": self.name,
			"location_space_id": self.location_space_id,
			"direction": self.direction,
			"inventory": self.inventory,
			"fuel": self.inventory.get(FUEL_ID, 0),
			"health": self.health,
			"damage": self.damage,
			"abilities": [ability.to_dict() for ability in self.abilities],
			"explored_spaces":self.explored_spaces
		}

		if game_state:
			data["named_inventory"] = get_named_inventory(self.inventory, game_state)

		return data

@dataclass  
class AutonomousUnit(Unit):
	"""
	Base class for AI-controlled units that act independently each turn.
	Extends Unit with autonomous behavior capabilities.
	"""
	lifespan: int = 50  # Turns remaining before unit expires
	state: str = "idle"  # Current AI state
	state_data: Dict[str, any] = field(default_factory=dict)  # State-specific data storage
	
	def advance_time(self, game_state):
		"""
		Called each turn to process autonomous behavior and update lifespan.
		"""
		# Decrease lifespan
		self.lifespan -= 1
		
		# Execute AI state logic
		self.execute_state_logic(game_state)
		
		# Handle expiration
		if self.lifespan <= 0:
			self.on_expiration(game_state)
	
	def execute_state_logic(self, game_state):
		"""
		Override in subclasses to implement specific AI behavior.
		Should handle state transitions and actions based on current state.
		"""
		pass
	
	def on_expiration(self, game_state):
		"""
		Called when unit expires. Override for custom expiration behavior.
		Default behavior is to mark for removal from game state.
		"""
		# Mark unit for removal (will be handled by game state manager)
		self.state = "expired"
	
	def change_state(self, new_state: str, state_data: Dict[str, any] = None):
		"""
		Change the unit's current state and optionally update state data.
		"""
		self.state = new_state
		if state_data:
			self.state_data.update(state_data)
	
	def to_dict(self, game_state=None):
		"""
		Convert to dictionary, including autonomous unit specific fields.
		"""
		data = super().to_dict(game_state)
		data.update({
			"lifespan": self.lifespan,
			"state": self.state,
			"state_data": self.state_data,
			"unit_type": "autonomous"
		})
		return data