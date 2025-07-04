from abc import ABC, abstractmethod
from typing import List, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class Container(ABC):
	id: str
	name: str
	location: Tuple[int, int]  # float for system-level, but overridden

	@abstractmethod
	def to_dict(self) -> dict:
		pass