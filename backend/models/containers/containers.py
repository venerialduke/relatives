from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Set, Optional
from models.containers.base import Container
from models.entities.entities import Unit, Structure, Resource
from utils.resource_management import InventoryMixin
from utils.location_management import space_distance, are_adjacent_spaces, first_n_spiral_hexes

@dataclass
class System(Container):
	bodies: List["Body"] = field(default_factory=list)
	gravity_wells: List[Dict] = field(default_factory=list)  # Just dicts for now

	def get_bodies(self):
		return self.bodies

	def get_gravity_wells(self):
		return self.gravity_wells

	def to_dict(self):
		return {
			"id": self.id,
			"name": self.name,
			"location": (self.q, self.r),
			"q": self.q,
			"r": self.r,
			"gravity_wells": self.gravity_wells,
			"bodies": [b.to_dict() for b in self.bodies]
		}

@dataclass
class Body(Container):
	system_id: Optional[str] = None
	spaces: List["Space"] = field(default_factory=list)

	def get_spaces(self):
		return self.spaces

	def to_dict(self):
		return {
			"id": self.id,
			"name": self.name,
			"system_id": self.system_id,
			"location": (self.q, self.r),
			"q": self.q,
			"r": self.r,
			"spaces": [s.to_dict() for s in self.spaces]
		}

	def _occupied_coords(self) -> Set[Tuple[int, int]]:
		return {s.get_relative_coords() for s in self.spaces}

	def get_next_space_coords(self, max_search=100):
		occupied = self._occupied_coords()
		for q, r in first_n_spiral_hexes(max_search):
			if (q, r) not in occupied:
				return q, r
		raise Exception("Could not find free space location.")

	def add_space(self, space: "Space"):
		occupied = self._occupied_coords()
		if space.get_relative_coords not in occupied:
			self.spaces.append(space)
			return

		raise Exception("Could not find free space to place new hex.")

@dataclass
class Space(Container, InventoryMixin):
	body_id: Optional[str] = None
	body_rel_q: int = 0
	body_rel_r: int = 0
	inventory: Dict[str, int] = field(default_factory=dict)
	structures: List[Structure] = field(default_factory=list)
	units: List[Unit] = field(default_factory=list)
	max_buildings: int = 1
	max_units: int = 2

	def get_relative_coords(self):
		return (self.body_rel_q, self.body_rel_r)
	
	def get_global_coords(self):
		return (self.q, self.r)

	def set_global_coords(self, body_q: int, body_r: int):
		self.q = body_q + self.body_rel_q
		self.r = body_r + self.body_rel_r

	def get_resources(self):
		return self.inventory 
	
	def get_structures(self):
		return self.structures 
	
	def get_units(self):
		return self.units

	def get_neighbors_within_radius(self, all_spaces: List["Space"], radius: int) -> List["Space"]:
		return [
			other for other in all_spaces
			if self.id != other.id and space_distance(self, other) <= radius
		]

	def is_adjacent_to(self, other: "Space") -> bool:
		return are_adjacent_spaces(self, other)

	def to_dict(self):
		return {
			"id": self.id,
			"body_id": self.body_id,
			"location": (self.q, self.r),
			"q": self.q,
			"r": self.r,
			"inventory": self.inventory,
			"body_rel_location": (self.body_rel_q, self.body_rel_r),
			"buildings": [s.to_dict() for s in self.structures],
			"units": [u.to_dict() for u in self.units]
		}
