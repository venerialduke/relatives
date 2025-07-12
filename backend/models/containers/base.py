from abc import ABC, abstractmethod
from typing import List, Tuple, Any
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Container(ABC):
	id: str
	name: str
	q: Optional[int] = None
	r: Optional[int] = None

	@abstractmethod
	def to_dict(self) -> dict:
		pass
	
	def advance_time(self,game_state):
		pass