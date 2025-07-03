from abc import ABC, abstractmethod


class Actor(ABC):
    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @property
    @abstractmethod
    def location_space_id(self) -> int:
        pass

    @property
    @abstractmethod
    def abilities(self) -> list:
        pass

