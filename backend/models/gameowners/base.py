# gameowner/base.py

# gameowner/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any
from models.entities.base import Actor
from models.entities.entities import Unit, Structure
from models.abilities.base import Ability
from models.containers.base import Container


@dataclass
class GameOwner(ABC):
    name: str
    description: str = ""
    entities: List[Actor] = field(default_factory=list)
    containers: List[Container] = field(default_factory=list)
    abilities: List[Ability] = field(default_factory=list)

    def get_units(self) -> List[Unit]:
        return [e for e in self.entities if e.__class__.__name__.lower() == "unit"]

    def get_structures(self) -> List[Structure]:
        return [e for e in self.entities if e.__class__.__name__.lower() == "structure"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "units": [u.to_dict() for u in self.get_units()],
            "structures": [s.to_dict() for s in self.get_structures()],
            "abilities": [a.to_dict() for a in self.abilities],
        }

    def owns_actor(self, actor: Actor) -> bool:
        return actor in self.entities

    def perform_unit_ability(self, actor_id, game_state, **kwargs): 
        actor = game_state.get_unit_by_id(actor_id)
        if actor is None:
            return f"Unit with ID {actor_id} not found."
        if not self.owns_actor(actor):
            return "Permission denied"
        
        ability_name = kwargs.get("ability")
        if not ability_name:
            return "No ability specified"

        return actor.perform_ability(ability_name, game_state, **kwargs)

    def perform_structure_ability(self, actor_id, game_state, **kwargs): 
        actor = game_state.get_structure_by_id(actor_id)
        if actor is None:
            return f"Structure with ID {actor_id} not found."
        if not self.owns_actor(actor):
            return "Permission denied"
        
        ability_name = kwargs.get("ability")
        if not ability_name:
            return "No ability specified"

        return actor.perform_ability(ability_name, game_state, **kwargs)
