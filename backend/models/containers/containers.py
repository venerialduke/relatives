from dataclasses import dataclass, field
from typing import Tuple, List, Dict
from containers.base import Container

@dataclass
class System(Container):
	id: int
	name: str
	location: Tuple[float, float]  # galaxy position
	bodies: List["Body"] = field(default_factory=list)
	gravity_wells: List[Dict] = field(default_factory=list)  # Just dicts for now

	def get_contents(self):
		return self.bodies

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

	def get_contents(self):
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
	resource_ids: List[int] = field(default_factory=list)
	building_ids: List[int] = field(default_factory=list)
	unit_ids: List[int] = field(default_factory=list)
	max_resources: int = 3
	max_buildings: int = 1
	max_units: int = 2

	def get_contents(self):
		return {
			"resources": self.resource_ids,
			"buildings": self.building_ids,
			"units": self.unit_ids
		}

	def to_dict(self):
		return {
			"id": self.id,
			"body_id": self.body_id,
			"location": self.location,
			"resources": self.resource_ids,
			"buildings": self.building_ids,
			"units": self.unit_ids
		}