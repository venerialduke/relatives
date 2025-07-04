# gameowner/player.py

from models.gameowners.base import GameOwner

class Player(GameOwner):
    def __init__(self, name: str, description: str = "", player_id: str = ""):
        super().__init__(name, description)
        self.player_id = player_id  # External reference (auth, socket ID, etc.)


class SystemManager(GameOwner):
    def __init__(self, system_id: int, name: str = "System", description: str = ""):
        super().__init__(name, description)
        self.system_id = system_id  # Which system this manager governs
