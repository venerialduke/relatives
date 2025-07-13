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
    "Scanner": {"Ore": 1, "Silicon": 1}
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