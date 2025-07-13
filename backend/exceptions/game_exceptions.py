"""
Game-specific exception classes for better error handling.
"""

class GameException(Exception):
    """Base exception for all game-related errors."""
    pass

class MovementException(GameException):
    """Raised when movement operations fail."""
    pass

class InsufficientFuelException(MovementException):
    """Raised when unit lacks fuel for movement."""
    pass

class InvalidLocationException(MovementException):
    """Raised when attempting to move to invalid location."""
    pass

class CollectionException(GameException):
    """Raised when resource collection fails."""
    pass

class InsufficientResourcesException(CollectionException):
    """Raised when not enough resources are available."""
    pass

class BuildingException(GameException):
    """Raised when building construction fails."""
    pass

class InvalidStructureTypeException(BuildingException):
    """Raised when trying to build unknown structure type."""
    pass

class EntityNotFoundException(GameException):
    """Raised when requested entity doesn't exist."""
    pass

class PermissionException(GameException):
    """Raised when player lacks permission for action."""
    pass

class GameStateException(GameException):
    """Raised when game state is invalid or corrupted."""
    pass