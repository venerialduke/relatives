from abc import ABC, abstractmethod
from typing import Any

class Ability(ABC):
    name: str
    description: str

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    @abstractmethod
    def perform(self, actor: Any, game_state: Any, **kwargs):
        """Executes the ability's action."""
        pass

    def to_dict(self):
        """Useful for sending ability info to frontend."""
        return {
            "name": self.name,
            "description": self.description,
        }
    
    def advance_time(self,game_state):
        pass