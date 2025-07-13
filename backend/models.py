"""
Legacy models import file.
For backwards compatibility - use specific module imports instead.
"""

# Core game state
from core.game_state import GameState

# Containers
from models.containers.containers import System, Body, Space

# Entities
from models.entities.entities import Unit, Structure, Resource
from models.entities.entity_content import PlayerUnit

# Abilities
from models.abilities.abilities import MoveAbility, CollectAbility, BuildAbility

# Game owners
from models.gameowners.owners import Player, SystemManager

# Configuration
from config.game_config import (
    FUEL_ID, RESOURCE_NAMES, STRUCTURE_REQUIREMENTS, 
    BODY_DEFINITIONS, HEX_DIRECTIONS
)

__all__ = [
    'GameState',
    'System', 'Body', 'Space',
    'Unit', 'Structure', 'Resource', 'PlayerUnit',
    'MoveAbility', 'CollectAbility', 'BuildAbility',
    'Player', 'SystemManager',
    'FUEL_ID', 'RESOURCE_NAMES', 'STRUCTURE_REQUIREMENTS',
    'BODY_DEFINITIONS', 'HEX_DIRECTIONS'
]