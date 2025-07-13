# Future Recipe System Concept

## Overview
This document captures the recipe-based approach for future implementation across all structures, not just Space Ports.

## Core Concept
Instead of fixed structure definitions, players can discover and use different "recipes" that create structures with varying capabilities.

## Architecture Framework

### Configuration Structure
```python
# Future: All structures support recipes
STRUCTURE_RECIPES = {
    "Collector": {
        "basic": {"efficiency": 1, "build_cost": {...}},
        "advanced": {"efficiency": 2, "build_cost": {...}}
    },
    "SpacePort": {
        "basic": {"travel_cost": 2, "build_cost": {...}},
        "advanced": {"travel_cost": 1, "build_cost": {...}},
        "cargo": {"travel_cost": 3, "cargo_bonus": 2, "build_cost": {...}}
    }
}
```

### Player Recipe Discovery
```python
class Player:
    discovered_recipes: Dict[str, List[str]]  # structure_type -> [recipe_names]
    
    def can_build_recipe(self, structure_type: str, recipe: str) -> bool:
        return recipe in self.discovered_recipes.get(structure_type, [])
```

### Structure Factory Pattern
```python
class Structure:
    @classmethod
    def create_from_recipe(cls, structure_type: str, recipe: str, **kwargs):
        recipe_config = STRUCTURE_RECIPES[structure_type][recipe]
        return cls(recipe_type=recipe, **recipe_config, **kwargs)
```

## Benefits
- **Player Progression**: Discover better recipes over time
- **Strategic Depth**: Different players have different capabilities  
- **Emergent Gameplay**: Unique combinations and specializations
- **Dynamic Balance**: Adjust recipes without code changes

## Implementation Phases (Future)
1. **Recipe Discovery System**: Research, exploration-based unlocks
2. **Recipe Storage**: Player persistent recipe collections
3. **Recipe Trading**: Players can share/trade recipes
4. **Recipe Crafting**: Combine recipes to create new ones

## Integration Points
- **Building System**: Recipe selection during construction
- **UI System**: Recipe browser and selection interface
- **Save System**: Persist discovered recipes
- **Balance System**: Recipe effectiveness tuning

*Save this concept for when we implement the full recipe system across all structures.*