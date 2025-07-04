from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Set
from models.containers.base import Container
from models.entities.entities import Unit, Structure, Resource
from utils.resource_management import InventoryMixin
from utils.location_management import space_distance, are_adjacent_spaces

@dataclass
class System(Container):
	id: str
	name: str
	location: Tuple[float, float]  # galaxy position
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
			"location": self.location,
			"gravity_wells": self.gravity_wells,
			"bodies": [b.to_dict() for b in self.bodies]
		}


@dataclass
class Body(Container):
	id: str
	system_id: str
	name: str
	location: Tuple[int, int]
	spaces: List["Space"] = field(default_factory=list)

	def get_spaces(self):
		return self.spaces

	def to_dict(self):
		return {
			"id": self.id,
			"name": self.name,
			"system_id": self.system_id,
			"location": self.location,
			"spaces": [s.to_dict() for s in self.spaces]
		}

	def _occupied_coords(self) -> Set[Tuple[int, int]]:
		return {(s.q, s.r) for s in self.spaces}

	def add_space(self, space: "Space"):
		"""
		Assigns a (q, r) coordinate in spiral hex order, then adds the space.
		"""
		occupied = self._occupied_coords()

		if not occupied:
			space.q, space.r = 0, 0
			self.spaces.append(space)
			return

		# Spiral walk from center outward
		directions = [(1, 0), (1, -1), (0, -1),
					  (-1, 0), (-1, 1), (0, 1)]

		for radius in range(1, 100):  # Safety limit
			q, r = 0, -radius
			for direction in range(6):
				for _ in range(radius):
					dq, dr = directions[direction]
					if (q, r) not in occupied:
						space.q, space.r = q, r
						self.spaces.append(space)
						return
					q += dq
					r += dr

		raise Exception("Could not find free space to place new hex.")

@dataclass
class Space(Container, InventoryMixin):
	id: str
	body_id: str
	q: int = 0
	r: int = 0
	inventory: Dict[str, int] = field(default_factory=dict)
	structures: List[Structure] = field(default_factory=list)
	units: List[Unit] = field(default_factory=list)
	max_buildings: int = 1
	max_units: int = 2

	def get_resources(self):
		return self.inventory 
	
	def get_structures(self):
		return self.structures 
	
	def get_units(self):
		return self.units

	def set_coords(self, q: int, r: int):
		self.q = q
		self.r = r

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
			"inventory": self.inventory,
			"q": self.q,
        	"r": self.r,
			"buildings": [s.to_dict() for s in self.structures],
			"units": [u.to_dict() for u in self.units]
		}
