from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from gamemonitors.monitors import GameState
     
class Actor(ABC):
    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @abstractmethod
    def location_space_id(self) -> str:
        pass

    @abstractmethod
    def abilities(self) -> list:
        pass

    def perform_ability(self, ability_name: str, game_state: 'GameState', **kwargs):
        for ability in self.abilities:
            if ability.name == ability_name:
                return ability.perform(self, game_state, **kwargs)
        return f"No ability named '{ability_name}' found."