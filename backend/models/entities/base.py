from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from gamemonitors.monitors import GameState
     
class Actor(ABC):
	@abstractmethod
	def to_dict(self) -> dict:
		pass

	@abstractmethod
	def abilities(self) -> list:
		pass

	@property
	@abstractmethod
	def location_space_id(self) -> str:
		pass

	@property
	@abstractmethod
	def explored_spaces(self) -> list:
		pass
	
    def advance_time(self,game_state):
        pass

	def mark_explored(self, space_id: str):
		if space_id not in self.explored_spaces:
			self.explored_spaces.append(space_id)
	
	def perform_ability(self, ability_name: str, game_state: 'GameState', **kwargs):
		for ability in self.abilities:
			if ability.name == ability_name:
				return ability.perform(self, game_state, **kwargs)
		return f"No ability named '{ability_name}' found."