"""
Game monitors module.
GameState has been moved to core.game_state for better architecture.
"""

# Import from new location for backwards compatibility
from core.game_state import GameState

# Legacy imports - use core.game_state directly
__all__ = ['GameState']