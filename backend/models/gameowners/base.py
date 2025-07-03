# gameowner/base.py

# gameowner/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any
from entities.base import Actor
from abilities.base import Ability
from containers.base import Container


@dataclass
class GameOwner(ABC):
    name: str
    description: str = ""
    entities: List[Actor] = field(default_factory=list)
    containers: List[Container] = field(default_factory=list)
    abilities: List[Ability] = field(default_factory=list)

    def get_units(self) -> List[Actor]:
        return [e for e in self.entities if e.__class__.__name__.lower() == "unit"]

    def get_structures(self) -> List[Actor]:
        return [e for e in self.entities if e.__class__.__name__.lower() == "structure"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "units": [u.to_dict() for u in self.get_units()],
            "structures": [s.to_dict() for s in self.get_structures()],
            "abilities": [a.to_dict() for a in self.abilities],
        }

    @abstractmethod
    def perform(self, actor_id: int, game_state: Any, **kwargs):
        """Delegates an action to one of the owner's actors."""
        pass
