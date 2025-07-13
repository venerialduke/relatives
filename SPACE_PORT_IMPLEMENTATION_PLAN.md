# Space Port Implementation Plan

## Overview

This document outlines the comprehensive implementation plan for adding Space Port structures to the Relatives game. Space Ports enable reduced-cost inter-body movement, creating a fast-travel network that enhances strategic gameplay.

## Requirements Analysis

### Core Functionality
- **New Structure Type**: Space Port as a buildable structure with configurable parameters
- **Reduced Cost Movement**: Inter-Space Port travel costs configurable fuel (default less than regular inter-body movement)
- **Recipe-Based Variations**: Different Space Port configurations with varying capabilities
- **Strategic Value**: Space Ports provide significant movement advantages based on their configuration

### Design Constraints
- **Integration**: Must work seamlessly with existing movement system
- **Balance**: Should not trivialize exploration or fuel management
- **Scalability**: Architecture should support future transportation features and recipe variations
- **User Experience**: Clear indication of Space Port routes and costs
- **Configurability**: Space Port parameters (cost, range, etc.) should be configurable per instance
- **Recipe System Ready**: Architecture should support different Space Port "recipes" with varying capabilities

## Technical Architecture

### Implementation Strategy: Enhanced Service Pattern

We'll use **Option 3: Enhanced Movement Service** because it:
- Leverages our existing service architecture
- Maintains clean separation of concerns
- Provides natural integration points
- Supports future transportation features

## Detailed Implementation Plan

### 1. Configuration Layer (`config/game_config.py`)

```python
# Space Port Configuration - Default Recipe
SPACE_PORT_DEFAULT_CONFIG = {
    "travel_cost": 2,  # Default fuel cost for Space Port to Space Port travel
    "regular_inter_body_cost": 5,  # Current cost (for comparison)
    "max_range": None,  # No range limit - any Space Port to any Space Port
    "network_id": "default",  # Default network
    "build_requirements": {
        "Silicon": 3,
        "Crystal": 2, 
        "Ore": 2,
        "SpaceDust": 1
    }
}

# Space Port Recipe System - Future recipes can have different parameters
SPACE_PORT_RECIPES = {
    "basic": {
        "travel_cost": 2,
        "build_requirements": {
            "Silicon": 3, "Crystal": 2, "Ore": 2, "SpaceDust": 1
        },
        "max_range": None,
        "network_id": "default"
    },
    # Future recipes:
    # "advanced": {
    #     "travel_cost": 1,  # More efficient
    #     "build_requirements": {
    #         "Silicon": 5, "Crystal": 4, "Ore": 3, "SpaceDust": 2, "Xenonite": 1
    #     },
    #     "max_range": None,
    #     "network_id": "advanced"
    # }
}

# Add to STRUCTURE_REQUIREMENTS (using default recipe)
STRUCTURE_REQUIREMENTS = {
    # ... existing structures ...
    "SpacePort": SPACE_PORT_DEFAULT_CONFIG["build_requirements"]
}
```

### 2. Space Port Structure (`models/entities/structures/space_port.py`)

```python
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from models.entities.entities import Structure
from config.game_config import SPACE_PORT_DEFAULT_CONFIG, SPACE_PORT_RECIPES

@dataclass
class SpacePort(Structure):
    """
    Space Port structure enabling fast inter-body travel.
    
    Space Ports form a network allowing reduced-cost movement between
    any connected Space Ports. Each Space Port has configurable parameters
    based on the recipe used to build it.
    """
    
    # Space Port specific properties - configurable per instance
    is_operational: bool = True
    travel_cost: int = field(default_factory=lambda: SPACE_PORT_DEFAULT_CONFIG["travel_cost"])
    network_id: str = field(default_factory=lambda: SPACE_PORT_DEFAULT_CONFIG["network_id"])
    max_range: Optional[int] = field(default_factory=lambda: SPACE_PORT_DEFAULT_CONFIG["max_range"])
    recipe_type: str = "basic"  # Which recipe was used to build this
    
    def __post_init__(self):
        super().__post_init__()
        self.structure_type = "SpacePort"
    
    @classmethod
    def create_from_recipe(cls, recipe_type: str, **kwargs) -> 'SpacePort':
        """Create a Space Port using a specific recipe configuration."""
        if recipe_type not in SPACE_PORT_RECIPES:
            recipe_type = "basic"  # Fallback to basic
        
        recipe = SPACE_PORT_RECIPES[recipe_type]
        
        # Override default values with recipe values
        space_port = cls(
            travel_cost=recipe["travel_cost"],
            network_id=recipe["network_id"],
            max_range=recipe.get("max_range"),
            recipe_type=recipe_type,
            **kwargs
        )
        
        return space_port
    
    def get_travel_cost(self) -> Optional[int]:
        """Get the fuel cost for traveling to/from this Space Port."""
        return self.travel_cost if self.is_operational else None
    
    def can_travel_to(self, destination_port: 'SpacePort') -> bool:
        """Check if travel to destination port is possible."""
        if not (self.is_operational and destination_port.is_operational):
            return False
        
        # Check network compatibility
        if self.network_id != destination_port.network_id:
            return False
        
        # Future: Check range limitations if max_range is set
        # if self.max_range is not None:
        #     distance = calculate_distance(self, destination_port)
        #     if distance > self.max_range:
        #         return False
        
        return True
    
    def get_recipe_info(self) -> Dict[str, Any]:
        """Get information about the recipe used for this Space Port."""
        return SPACE_PORT_RECIPES.get(self.recipe_type, SPACE_PORT_RECIPES["basic"])
    
    def to_dict(self, game_state=None) -> Dict[str, Any]:
        data = super().to_dict(game_state)
        data.update({
            "is_operational": self.is_operational,
            "network_id": self.network_id,
            "travel_cost": self.get_travel_cost(),
            "max_range": self.max_range,
            "recipe_type": self.recipe_type,
            "recipe_info": self.get_recipe_info(),
            "structure_type": "SpacePort"
        })
        return data
    
    def advance_time(self, game_state):
        """Space Port time advancement - could handle maintenance, etc."""
        super().advance_time(game_state)
        # Future: Add maintenance requirements, power consumption, etc.
        # Different recipes might have different maintenance needs
```

### 3. Space Port Network Service (`services/space_port_service.py`)

```python
from typing import List, Dict, Optional, Tuple
from core.game_state import GameState
from models.entities.structures.space_port import SpacePort
from exceptions.game_exceptions import EntityNotFoundException

class SpacePortService:
    """Service for managing Space Port networks and routing."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
    
    def get_space_ports(self) -> List[SpacePort]:
        """Get all Space Port structures in the game."""
        return [
            structure for structure in self.game_state.structures.values()
            if isinstance(structure, SpacePort)
        ]
    
    def get_accessible_space_ports(self, unit) -> List[SpacePort]:
        """Get Space Ports accessible to a specific unit."""
        accessible_spaces = self.game_state.get_all_accessible_spaces_for_unit(unit)
        accessible_ports = []
        
        for port in self.get_space_ports():
            if port.location_space_id in accessible_spaces and port.is_operational:
                accessible_ports.append(port)
        
        return accessible_ports
    
    def find_space_port_at_space(self, space_id: str) -> Optional[SpacePort]:
        """Find a Space Port at a specific space."""
        for port in self.get_space_ports():
            if port.location_space_id == space_id:
                return port
        return None
    
    def get_space_port_routes(self, from_space_id: str, unit) -> List[Dict]:
        """Get all available Space Port routes from a location."""
        # Check if current location has a Space Port
        origin_port = self.find_space_port_at_space(from_space_id)
        if not origin_port or not origin_port.is_operational:
            return []
        
        # Get all accessible destination ports
        accessible_ports = self.get_accessible_space_ports(unit)
        routes = []
        
        for dest_port in accessible_ports:
            if dest_port.id != origin_port.id and origin_port.can_travel_to(dest_port):
                # Get destination space info
                dest_space = self.game_state.get_space_by_id(dest_port.location_space_id)
                dest_body = self.game_state.get_body_by_id(dest_space.body_id) if dest_space else None
                
                routes.append({
                    "destination_space_id": dest_port.location_space_id,
                    "destination_space_name": dest_space.name if dest_space else "Unknown",
                    "destination_body_name": dest_body.name if dest_body else "Unknown",
                    "fuel_cost": origin_port.get_travel_cost(),
                    "travel_type": "space_port",
                    "space_port_id": dest_port.id
                })
        
        return routes
    
    def validate_space_port_travel(self, unit, from_space_id: str, to_space_id: str) -> Tuple[bool, str]:
        """Validate if Space Port travel is possible."""
        # Check origin Space Port
        origin_port = self.find_space_port_at_space(from_space_id)
        if not origin_port:
            return False, "No Space Port at origin location"
        
        if not origin_port.is_operational:
            return False, "Origin Space Port is not operational"
        
        # Check destination Space Port
        dest_port = self.find_space_port_at_space(to_space_id)
        if not dest_port:
            return False, "No Space Port at destination location"
        
        if not dest_port.is_operational:
            return False, "Destination Space Port is not operational"
        
        # Check if ports can connect
        if not origin_port.can_travel_to(dest_port):
            return False, "Space Ports are not on the same network"
        
        # Check if destination is accessible to unit
        accessible_ports = self.get_accessible_space_ports(unit)
        if dest_port not in accessible_ports:
            return False, "Destination Space Port not accessible"
        
        # Check fuel
        travel_cost = origin_port.get_travel_cost()
        from config.game_config import FUEL_ID
        current_fuel = unit.inventory.get(FUEL_ID, 0)
        if current_fuel < travel_cost:
            return False, f"Insufficient fuel (need {travel_cost}, have {current_fuel})"
        
        return True, "Space Port travel validated"
```

### 4. Building Validation Enhancement (`services/building_service.py`)

```python
# Add to BuildingService class

def _validate_build_location(self, player: Player, unit: PlayerUnit) -> bool:
    """
    Validate that the player can build at the unit's current location.
    Checks if the space is in the player's explored spaces.
    """
    current_space_id = unit.location_space_id
    
    # Check if space is in player's explored spaces
    player_explored_spaces = set()
    for owned_unit in player.entities:
        if hasattr(owned_unit, 'explored_spaces'):
            player_explored_spaces.update(owned_unit.explored_spaces)
    
    # Also include system-wide accessible spaces
    system_accessible = set(self.game_state.system_wide_accessible_spaces)
    all_accessible = player_explored_spaces.union(system_accessible)
    
    return current_space_id in all_accessible

def build_structure(
    self,
    player: Player,
    unit_id: str,
    structure_type: str,
    recipe_type: str = "basic"  # Add recipe parameter
) -> Dict[str, Any]:
    """Enhanced to support recipe-based construction and location validation."""
    
    # Validate unit
    unit = self._validate_unit(player, unit_id)
    
    # Validate build location
    if not self._validate_build_location(player, unit):
        raise BuildingException("Cannot build on unexplored space")
    
    # Handle Space Port recipe-based construction
    if structure_type == "SpacePort":
        return self._build_space_port(player, unit, recipe_type)
    
    # Handle regular structures
    return self._build_regular_structure(player, unit, structure_type)

def _build_space_port(
    self, 
    player: Player, 
    unit: PlayerUnit, 
    recipe_type: str
) -> Dict[str, Any]:
    """Build a Space Port using a specific recipe."""
    from config.game_config import SPACE_PORT_RECIPES
    
    if recipe_type not in SPACE_PORT_RECIPES:
        raise InvalidStructureTypeException(f"Unknown Space Port recipe: {recipe_type}")
    
    recipe = SPACE_PORT_RECIPES[recipe_type]
    resource_cost = self._convert_resource_requirements(recipe["build_requirements"])
    
    # Check if player has the recipe (future: recipe discovery system)
    # For now, all players have access to "basic" recipe
    if recipe_type != "basic":
        raise BuildingException(f"Recipe '{recipe_type}' not available")
    
    # Perform the build using the unit's BuildAbility with recipe info
    result = player.perform_unit_ability(
        actor_id=unit.id,
        game_state=self.game_state,
        ability="build",
        structure_type="SpacePort",
        recipe_type=recipe_type,
        resource_cost=resource_cost
    )
    
    if isinstance(result, str) and (
        result.startswith("Cannot build") or 
        result.startswith("Insufficient") or
        "not enough" in result.lower()
    ):
        raise BuildingException(result)
    
    # Get updated space information
    space = self.game_state.get_space_by_id(unit.location_space_id)
    
    return {
        "result": result,
        "recipe_type": recipe_type,
        "unit": unit.to_dict(game_state=self.game_state),
        "space": space.to_dict(game_state=self.game_state) if space else None
    }
```

### 5. Enhanced Movement Service Integration

```python
# Add to MovementService class in services/movement_service.py

from services.space_port_service import SpacePortService

class MovementService:
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.space_port_service = SpacePortService(game_state)  # Add this
    
    def get_movement_options(self, unit_id: str) -> Dict[str, Any]:
        """Enhanced to include Space Port routes with their specific costs."""
        unit = self.game_state.get_unit_by_id(unit_id)
        if not unit:
            raise EntityNotFoundException(f"Unit {unit_id} not found")
        
        current_space = self.game_state.get_space_by_id(unit.location_space_id)
        if not current_space:
            raise InvalidLocationException("Current space not found")
        
        # Get regular inter-body movement options
        regular_options = self._get_regular_movement_options(unit, current_space)
        
        # Get Space Port routes with individual costs
        space_port_routes = self.space_port_service.get_space_port_routes(
            current_space.id, unit
        )
        
        return {
            "regular_movement": regular_options,
            "space_port_routes": space_port_routes,
            "current_fuel": unit.inventory.get(FUEL_ID, 0),
            "costs": {
                "regular_inter_body": INTER_BODY_FUEL_COST,
                "local_movement": LOCAL_MOVEMENT_FUEL_COST
            }
        }
    
    def _handle_direct_movement(self, unit, current_space, target_space_id: str):
        """Enhanced to handle Space Port travel with configurable costs."""
        destination = self.game_state.get_space_by_id(target_space_id)
        if not destination:
            raise InvalidLocationException("Target space not found")
        
        # Check if this is Space Port travel
        is_space_port_travel, message = self.space_port_service.validate_space_port_travel(
            unit, current_space.id, target_space_id
        )
        
        if is_space_port_travel:
            # Get the specific Space Port travel cost (configurable per Space Port)
            origin_port = self.space_port_service.find_space_port_at_space(current_space.id)
            required_fuel = origin_port.get_travel_cost()
        else:
            # Use regular inter-body travel cost
            required_fuel = INTER_BODY_FUEL_COST
        
        # Check fuel
        current_fuel = unit.inventory.get(FUEL_ID, 0)
        if current_fuel < required_fuel:
            raise InsufficientFuelException(
                f"Insufficient fuel for movement (need {required_fuel}, have {current_fuel})"
            )
        
        return destination
```

### 5. Structure Registration Update

```python
# Update models/entities/structure_map.py

from models.entities.structures.space_port import SpacePort

STRUCTURE_CLS_MAP = {
    # ... existing structures ...
    "SpacePort": SpacePort,
}

def get_structure_class_by_type(structure_type: str):
    return STRUCTURE_CLS_MAP.get(structure_type)
```

### 6. API Enhancements

```python
# Add to app.py

@app.route('/api/space_port_routes/<unit_id>')
def get_space_port_routes(unit_id):
    """Get available Space Port routes for a unit."""
    try:
        unit = game_state.get_unit_by_id(unit_id)
        if not unit:
            return jsonify({"error": "Unit not found"}), 404
        
        space_port_service = SpacePortService(game_state)
        routes = space_port_service.get_space_port_routes(unit.location_space_id, unit)
        
        return jsonify({
            "routes": routes,
            "current_location": unit.location_space_id
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get Space Port routes: {str(e)}"}), 500

@app.route('/api/space_ports')
def get_all_space_ports():
    """Get information about all Space Ports."""
    try:
        space_port_service = SpacePortService(game_state)
        ports = space_port_service.get_space_ports()
        
        return jsonify({
            "space_ports": [port.to_dict(game_state) for port in ports],
            "total_count": len(ports)
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get Space Ports: {str(e)}"}), 500
```

## Implementation Phases

### Phase 1: Core Structure (2-3 hours)
1. Add Space Port configuration to `game_config.py`
2. Create `SpacePort` structure class
3. Update structure registration and building requirements
4. Test Space Port construction through existing building API

### Phase 2: Network Service (3-4 hours)  
1. Create `SpacePortService` class
2. Implement Space Port discovery and routing logic
3. Add validation for Space Port travel
4. Unit tests for service functionality

### Phase 3: Movement Integration (2-3 hours)
1. Enhance `MovementService` with Space Port logic
2. Update movement options API to include Space Port routes
3. Modify movement execution to handle Space Port travel costs
4. Integration tests for movement system

### Phase 4: API & Frontend (3-4 hours)
1. Add new API endpoints for Space Port information
2. Update frontend movement UI to show Space Port routes
3. Add visual indicators for Space Port structures on map
4. Update movement modal to handle Space Port options

### Phase 5: Testing & Polish (2-3 hours)
1. Comprehensive testing of Space Port network
2. Balance testing for fuel costs and strategic impact
3. UI/UX refinements
4. Documentation updates

## Strategic Implications

### Gameplay Impact
- **Early Game**: Space Ports are expensive, creating interesting build priorities
- **Mid Game**: First Space Port networks enable faster exploration  
- **Late Game**: Extensive networks and advanced recipes enable complex strategies
- **Recipe Progression**: Players work toward more efficient Space Port designs

### Balance Considerations
- **Build Cost**: Expensive enough to be strategic decisions, scales with recipe advancement
- **Travel Cost**: Configurable per Space Port - basic is cheaper than regular travel, advanced recipes even more efficient
- **Location Validation**: Can only build on explored spaces, maintaining exploration value
- **Recipe Availability**: Future system will gate advanced recipes behind research/discovery

### Recipe System Implications
- **Basic Recipe**: Available to all players, moderate efficiency (2 fuel cost)
- **Advanced Recipes**: Future unlock system, higher build cost but better efficiency (1 fuel cost)
- **Network Segregation**: Different recipes may create separate networks, enabling factional gameplay
- **Specialization**: Some recipes might have range limits, cargo restrictions, or special abilities

### Future Extensions
- **Recipe Discovery**: Find/research new Space Port designs with different capabilities
- **Network Warfare**: Disrupt enemy Space Port networks, protect your own
- **Maintenance Requirements**: Advanced Space Ports need periodic resource investment
- **Capacity Limits**: Higher-tier recipes support more simultaneous travelers
- **Special Cargo**: Some resources can only be transported via specific Space Port types
- **Range Limitations**: Some recipes have maximum travel distance
- **Network Hierarchies**: Express networks, local networks, cargo vs passenger networks

## Testing Strategy

### Unit Tests
```python
def test_space_port_construction():
    # Test Space Port can be built with correct resources
    
def test_space_port_network_discovery():
    # Test Space Port routes are discovered correctly
    
def test_space_port_travel_validation():
    # Test fuel requirements and accessibility
```

### Integration Tests
```python
def test_space_port_movement_integration():
    # Test complete flow from Space Port selection to movement
    
def test_space_port_vs_regular_movement():
    # Test cost differences and route selection
```

### Game Balance Tests
```python
def test_space_port_strategic_value():
    # Verify Space Ports provide meaningful advantage without breaking balance
```

## Success Criteria

1. **Functional**: Space Ports can be built and used for reduced-cost travel
2. **Integrated**: Seamless integration with existing movement system
3. **Balanced**: Provides strategic value without trivializing fuel management
4. **Extensible**: Architecture supports future transportation features
5. **User-Friendly**: Clear UI indication of Space Port routes and costs

## Risk Mitigation

### Technical Risks
- **Complexity**: Phased implementation reduces integration complexity
- **Performance**: Service layer enables efficient caching of routes
- **Bugs**: Comprehensive testing strategy catches edge cases

### Game Design Risks
- **Balance**: Conservative fuel costs maintain strategic tension
- **Complexity**: Optional feature doesn't impact core gameplay loop
- **Power Creep**: Limited to transportation, doesn't affect other systems

This implementation plan leverages our service architecture to add Space Ports as a natural extension of the existing game systems while maintaining clean code organization and enabling future transportation features.