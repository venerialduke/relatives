"""
Centralized game configuration and constants.
Single source of truth for all game settings.
"""

# Resource Configuration
FUEL_ID = 'fuel'

RESOURCE_NAMES = [
    "Iron", "Crystal", "Gas", "Ice", "Silver", "Algae",
    "Silicon", "Copper", "Sand", "Carbon", "Nickel", "Stone",
    "Obsidian", "Quartz", "Dust", "Water", "Oil", "Fish",
    "Plasma", "Fungus", "Xenonite", "Ore", "SpaceDust"
]

# Structure Configuration
STRUCTURE_REQUIREMENTS = {
    "Collector": {"Silver": 2, "Ore": 1},
    "Factory": {"Algae": 2, "SpaceDust": 3},
    "Settlement": {"Fungus": 4},
    "FuelPump": {"Ore": 2, "Crystal": 1},
    "Scanner": {"Ore": 1, "Silicon": 1},
    "SpacePort": {"Silicon": 3, "Crystal": 2, "Ore": 2, "SpaceDust": 1}
}

# World Generation Configuration
BODY_DEFINITIONS = [
    ("Planet 1", 20),
    ("Planet 2", 35),
    ("Planet 3", 30),
    ("Asteroid Clump", 10),
    ("Moon 1", 15),
    ("Comet", 10),
    ("Planet 4", 50)
]

# Movement Configuration
HEX_DIRECTIONS = [
    (1, 0),   # 0 - E
    (1, -1),  # 1 - NE
    (0, -1),  # 2 - NW
    (-1, 0),  # 3 - W
    (-1, 1),  # 4 - SW
    (0, 1)    # 5 - SE
]

# Fuel and Movement Costs
INTER_BODY_FUEL_COST = 5
LOCAL_MOVEMENT_FUEL_COST = 1
SPACE_PORT_TRAVEL_COST = 2  # Space Port to Space Port travel cost

# Starting Inventory Configuration
def get_starting_inventory_requirements():
    """Calculate resource requirements for starting inventory."""
    return {
        "Silver": 2,    # Collector
        "Algae": 2,     # Factory
        "Silicon": 1,   # Scanner
        "Fungus": 4,    # Settlement
        "Ore": 4,       # Collector (1) + FuelPump (2) + Scanner (1)
        "SpaceDust": 3, # Factory
        "Crystal": 1,   # FuelPump
        FUEL_ID: 10     # Starting fuel
    }

# World Generation Settings
WORLD_GENERATION = {
    "radius_between_bodies": 2,
    "max_placement_attempts": 100,
    "resource_count_range": (1, 4),
}

# Game Balance Settings
GAME_BALANCE = {
    "starting_fuel": 10,
    "fuel_pump_generation_rate": 1,  # Per time tick
    "max_resources_per_space": 4,
}

# Unit Build Costs Configuration
UNIT_BUILD_COSTS = {
    "mining_drone": {
        "iron": 10,
        "fuel": 5
    }
}

# Mining Drone Configuration
MINING_DRONE_CONFIG = {
    "default_lifespan": 30,
    "default_cargo_capacity": 10,
    "fuel_consumption_per_move": 1,
    "fuel_per_collection": 0,  # No fuel cost for collecting
    "default_target_resource": "iron",
    "search_radius": 15,
    "collection_efficiency": 1  # Resources collected per turn
}

# Collection Structures Configuration
COLLECTION_STRUCTURES = [
    "Factory",
    "SpacePort",
    "Collector"  # Future: when Collector gets collection capabilities
]

# Autonomous Unit Configuration
AUTONOMOUS_UNIT_CONFIG = {
    "max_autonomous_units_per_player": 50,
    "expiration_cleanup_threshold": 5,  # Remove units with lifespan <= this
    "ai_processing_enabled": True,
    "ai_error_tolerance": 3  # Max AI errors before unit is disabled
}