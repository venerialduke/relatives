from abc import ABC, abstractmethod
from typing import List, Tuple, Any
from dataclasses import dataclass, field

class Container(ABC):
	id: int
	name: str
	location: Tuple[int, int]  # or float for galaxy-level

	@abstractmethod
	def get_contents(self) -> List[Any]:
		pass

	@abstractmethod
	def to_dict(self) -> dict:
		pass