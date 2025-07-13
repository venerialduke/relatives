# Simple Space Port Implementation Plan

## Overview
Implement Space Ports following existing structure patterns - simple, clean, and consistent with current architecture.

## Core Requirements
- **New Structure**: Space Port as buildable structure (like Collector, Factory, etc.)
- **Network Travel**: Reduced-cost movement between Space Ports
- **Existing Patterns**: Follow current structure implementation approach
- **Service Integration**: Clean integration with MovementService

## Implementation Plan

### 1. Configuration Addition (`config/game_config.py`)

```python
# Add to existing STRUCTURE_REQUIREMENTS
STRUCTURE_REQUIREMENTS = {
    "Collector": {"Silver": 2, "Ore": 1},
    "Factory": {"Algae": 2, "SpaceDust": 3},
    "Settlement": {"Fungus": 4},
    "FuelPump": {"Ore": 2, "Crystal": 1},
    "Scanner": {"Ore": 1, "Silicon": 1},
    "SpacePort": {"Silicon": 3, "Crystal": 2, "Ore": 2, "SpaceDust": 1}  # Add this
}

# Add Space Port specific config
SPACE_PORT_TRAVEL_COST = 2  # Fuel cost for Space Port travel (vs 5 for regular inter-body)
```

### 2. Space Port Structure (`models/entities/structures/space_port.py`)

```python
from dataclasses import dataclass
from typing import Dict, Any, Optional
from models.entities.entities import Structure
from config.game_config import SPACE_PORT_TRAVEL_COST

@dataclass
class SpacePort(Structure):
    """
    Space Port structure enabling reduced-cost inter-body travel.
    Simple implementation following existing structure patterns.
    """
    
    is_operational: bool = True
    
    def __post_init__(self):
        super().__post_init__()
        self.structure_type = "SpacePort"
    
    def get_travel_cost(self) -> Optional[int]:
        """Get fuel cost for traveling to/from this Space Port."""
        return SPACE_PORT_TRAVEL_COST if self.is_operational else None
    
    def can_connect_to(self, other_port: 'SpacePort') -> bool:
        """Check if this Space Port can connect to another."""
        return self.is_operational and other_port.is_operational
    
    def to_dict(self, game_state=None) -> Dict[str, Any]:
        data = super().to_dict(game_state)
        data.update({
            "is_operational": self.is_operational,
            "travel_cost": self.get_travel_cost(),
            "structure_type": "SpacePort"
        })
        return data
    
    def advance_time(self, game_state):
        """Space Port time advancement."""
        super().advance_time(game_state)
        # Future: maintenance, operational status changes, etc.
```

### 3. Structure Registration (`models/entities/structure_map.py`)

```python
# Add to existing structure map
from models.entities.structures.space_port import SpacePort

STRUCTURE_CLS_MAP = {
    "Collector": Collector,
    "Factory": Factory, 
    "Settlement": Settlement,
    "FuelPump": FuelPump,
    "Scanner": Scanner,
    "SpacePort": SpacePort  # Add this
}
```

### 4. Space Port Service (`services/space_port_service.py`)

```python
from typing import List, Dict, Optional
from core.game_state import GameState
from models.entities.structures.space_port import SpacePort
from config.game_config import SPACE_PORT_TRAVEL_COST

class SpacePortService:
    """Simple service for Space Port network operations."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
    
    def get_all_space_ports(self) -> List[SpacePort]:
        """Get all Space Port structures."""
        return [
            structure for structure in self.game_state.structures.values()
            if isinstance(structure, SpacePort)
        ]
    
    def get_accessible_space_ports(self, unit) -> List[SpacePort]:
        """Get Space Ports accessible to a unit."""
        accessible_spaces = self.game_state.get_all_accessible_spaces_for_unit(unit)
        return [
            port for port in self.get_all_space_ports()
            if port.location_space_id in accessible_spaces and port.is_operational
        ]
    
    def find_space_port_at_space(self, space_id: str) -> Optional[SpacePort]:
        """Find Space Port at a specific space."""
        for port in self.get_all_space_ports():
            if port.location_space_id == space_id:
                return port
        return None
    
    def get_space_port_destinations(self, from_space_id: str, unit) -> List[Dict]:
        """Get available Space Port destinations from current location."""
        origin_port = self.find_space_port_at_space(from_space_id)
        if not origin_port or not origin_port.is_operational:
            return []
        
        destinations = []
        accessible_ports = self.get_accessible_space_ports(unit)
        
        for dest_port in accessible_ports:
            if dest_port.id != origin_port.id and origin_port.can_connect_to(dest_port):
                dest_space = self.game_state.get_space_by_id(dest_port.location_space_id)
                dest_body = self.game_state.get_body_by_id(dest_space.body_id) if dest_space else None
                
                destinations.append({
                    "space_id": dest_port.location_space_id,
                    "space_name": dest_space.name if dest_space else "Unknown",
                    "body_name": dest_body.name if dest_body else "Unknown", 
                    "fuel_cost": SPACE_PORT_TRAVEL_COST,
                    "travel_type": "space_port"
                })
        
        return destinations
    
    def validate_space_port_travel(self, unit, from_space_id: str, to_space_id: str) -> tuple[bool, str]:
        """Validate Space Port travel between two spaces."""
        # Check origin
        origin_port = self.find_space_port_at_space(from_space_id)
        if not origin_port or not origin_port.is_operational:
            return False, "No operational Space Port at origin"
        
        # Check destination  
        dest_port = self.find_space_port_at_space(to_space_id)
        if not dest_port or not dest_port.is_operational:
            return False, "No operational Space Port at destination"
        
        # Check accessibility
        accessible_ports = self.get_accessible_space_ports(unit)
        if dest_port not in accessible_ports:
            return False, "Destination Space Port not accessible"
        
        # Check fuel
        from config.game_config import FUEL_ID
        current_fuel = unit.inventory.get(FUEL_ID, 0)
        if current_fuel < SPACE_PORT_TRAVEL_COST:
            return False, f"Insufficient fuel (need {SPACE_PORT_TRAVEL_COST}, have {current_fuel})"
        
        return True, "Space Port travel valid"
```

### 5. Movement Service Integration (`services/movement_service.py`)

```python
# Add to existing MovementService class

from services.space_port_service import SpacePortService
from config.game_config import SPACE_PORT_TRAVEL_COST

class MovementService:
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.space_port_service = SpacePortService(game_state)  # Add this
    
    def get_movement_options(self, unit_id: str) -> Dict[str, Any]:
        """Enhanced to include Space Port options."""
        # ... existing code ...
        
        # Add Space Port destinations
        space_port_destinations = self.space_port_service.get_space_port_destinations(
            current_space.id, unit
        )
        
        result = {
            "reachable_bodies": reachable_bodies,  # existing regular movement
            "space_port_destinations": space_port_destinations,  # new Space Port routes
            "current_fuel": current_fuel,
            "costs": {
                "inter_body_cost": 5,
                "space_port_cost": SPACE_PORT_TRAVEL_COST
            }
        }
        
        return result
    
    def _handle_direct_movement(self, unit, current_space, target_space_id: str):
        """Enhanced to detect and handle Space Port travel."""
        destination = self.game_state.get_space_by_id(target_space_id)
        if not destination:
            raise InvalidLocationException("Target space not found")
        
        # Check if this is Space Port travel
        is_space_port_travel, message = self.space_port_service.validate_space_port_travel(
            unit, current_space.id, target_space_id
        )
        
        # Determine fuel cost
        if is_space_port_travel:
            required_fuel = SPACE_PORT_TRAVEL_COST
        else:
            required_fuel = INTER_BODY_FUEL_COST  # Regular inter-body travel
        
        # Check fuel
        current_fuel = unit.inventory.get(FUEL_ID, 0)
        if current_fuel < required_fuel:
            raise InsufficientFuelException(
                f"Insufficient fuel (need {required_fuel}, have {current_fuel})"
            )
        
        return destination
```

### 6. API Enhancement (`app.py`)

```python
# Add new endpoint for Space Port information
@app.route('/api/space_port_destinations/<unit_id>')
def get_space_port_destinations(unit_id):
    """Get Space Port destinations for a unit."""
    try:
        unit = game_state.get_unit_by_id(unit_id)
        if not unit:
            return jsonify({"error": "Unit not found"}), 404
        
        from services.space_port_service import SpacePortService
        space_port_service = SpacePortService(game_state)
        destinations = space_port_service.get_space_port_destinations(
            unit.location_space_id, unit
        )
        
        return jsonify({"destinations": destinations})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

## Implementation Phases

### Phase 1: Core Structure (2 hours)
1. Add Space Port to config and structure map
2. Create simple SpacePort class
3. Test building through existing API

### Phase 2: Network Service (2 hours)  
1. Create SpacePortService
2. Implement destination discovery
3. Add travel validation

### Phase 3: Movement Integration (2 hours)
1. Enhance MovementService 
2. Update movement options API
3. Test Space Port travel

### Phase 4: Frontend & Polish (2 hours)
1. Update UI to show Space Port destinations
2. Add Space Port visual indicators
3. Testing and refinement

**Total: ~8 hours** (vs 12-15 for recipe approach)

## Key Differences from Recipe Approach

### Simpler Architecture
- **Single travel cost** for all Space Ports (configurable globally)
- **No recipe system** - follows existing structure patterns
- **Direct integration** with existing building system

### Following Existing Patterns
- **Structure Requirements**: Like Collector, Factory, etc.
- **Class Structure**: Extends Structure like other buildings
- **Building Process**: Uses existing BuildAbility system
- **Configuration**: Simple constants in game_config.py

### Future Extension Points
- **Operational Status**: Can be enhanced later (maintenance, power, etc.)
- **Network Improvements**: Can add network IDs, range limits later
- **Recipe Integration**: When we implement recipes for all structures

## Benefits
- **Quick Implementation**: Follows known patterns
- **Low Risk**: Minimal changes to existing systems
- **Consistent**: Matches current structure implementation
- **Extensible**: Can be enhanced with recipe system later

This approach gets Space Ports working quickly while staying consistent with our current architecture. When we implement the full recipe system, Space Ports can be upgraded along with all other structures.