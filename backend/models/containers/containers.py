from dataclasses import dataclass, field
from typing import Tuple, List, Dict
from models.containers.base import Container
from models.entities.entities import Unit, Structure, Resource

@dataclass
class System(Container):
	id: int
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
	id: int
	system_id: int
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
	
@dataclass
class Space(Container):
	id: int
	body_id: int
	location: Tuple[int, int]
	resources: List[Dict[str, int]] = field(default_factory=list)  # [{resource_id: int, quantity: int}]
	structures: List[Structure] = field(default_factory=list)
	units: List[Unit] = field(default_factory=list)
	max_resources: int = 3
	max_buildings: int = 1
	max_units: int = 2

	def get_resources(self):
		return self.resources 
	
	def get_structures(self):
		return self.structures 
	
	def get_units(self):
		return self.units

	def to_dict(self):
		return {
			"id": self.id,
			"body_id": self.body_id,
			"location": self.location,
			"resources": self.resources,
			"buildings": [s.to_dict() for s in self.structures],
			"units": [u.to_dict() for u in self.units]
		}
