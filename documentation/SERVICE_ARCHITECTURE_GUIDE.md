# Service Architecture Guide - Professional Game Development

## Overview

This guide explains the Service Layer architecture implemented in the Relatives game project. The Service Layer is a **Domain Service** pattern that encapsulates business logic and provides the foundation for professional game development.

## What Services Actually Do

The Service Layer acts as a bridge between your API and game logic, but it's much more than just a "helper layer":

```
Frontend → API Endpoints → Services → Abilities → Game State
```

Services provide **business logic orchestration**, **data transformation**, **validation**, and **transaction boundaries** that are essential for maintainable game architecture.

## The Four Pillars of Service Architecture

### 1. Business Logic Orchestration

Services coordinate complex operations that involve multiple game systems:

```python
# Example: BuildingService.build_structure()
def build_structure(self, player, unit_id, structure_type):
    # 1. Validate player owns unit
    unit = self._validate_unit(player, unit_id)
    
    # 2. Check structure type exists
    resource_cost = self._validate_structure_type(structure_type)
    
    # 3. Convert resource names to IDs
    converted_cost = self._convert_resource_requirements(resource_cost)
    
    # 4. Execute through ability system
    result = player.perform_unit_ability(...)
    
    # 5. Handle structured responses
    return formatted_result
```

This **orchestration logic** doesn't belong in the API (too high-level) or in Abilities (too low-level). Services are the perfect middle ground.

### 2. Data Transformation & Validation

Services handle the "impedance mismatch" between different layers:

- **API layer**: Receives JSON with strings, user input
- **Ability layer**: Expects validated objects, IDs, game entities

```python
# CollectionService transforms and validates:
resource_input = "Iron"  # From API
↓
resource_id = "res_1"    # For abilities
↓ 
validated_unit = PlayerUnit(...)  # Game object
```

### 3. Cross-Cutting Concerns

Services handle concerns that span multiple abilities:

- **Permission checking**: "Does this player own this unit?"
- **Resource validation**: "Does this resource exist?"
- **State consistency**: "Is the game state valid for this operation?"
- **Error translation**: Convert game errors to API-appropriate responses

### 4. Transaction Boundaries

Services define **what constitutes a complete operation**:

```python
def move_unit(self, player, unit_id, direction, target_space_id):
    # This is ONE logical operation that might involve:
    # - Fuel consumption
    # - Location updates  
    # - Exploration tracking
    # - State synchronization
    
    # If ANY part fails, the whole operation should fail
```

## Strategic Value: Why This Architecture Matters

### Testing Isolation

**Without services** - testing requires setting up the entire Flask app:

```python
# BAD: Testing through Flask endpoints
def test_movement():
    with app.test_client() as client:
        response = client.post('/api/move_unit', json={...})
        # Tests HTTP, JSON parsing, Flask routing, business logic all together
```

**With services** - test pure business logic:

```python
# GOOD: Testing pure business logic
def test_movement():
    game_state = GameState()
    service = MovementService(game_state)
    result = service.move_unit(...)  # Direct business logic test
```

### Multiple API Frontends

Services let you support different interfaces using the same business logic:

```python
# Same business logic, different interfaces:
# - REST API (current Flask app)
# - GraphQL API
# - WebSocket real-time API  
# - Admin CLI tools
# - Mobile app API

# All use the same MovementService.move_unit()
```

### Feature Composition

Services enable complex features by composing simple operations:

```python
# Future: "Auto-collect and build" feature
class AutomationService:
    def __init__(self, collection_service, building_service):
        self.collection = collection_service
        self.building = building_service
    
    def auto_build_collector(self, player, unit_id):
        # 1. Collect required resources
        self.collection.collect_resource(...)
        # 2. Build structure
        self.building.build_structure(...)
        # Complex operation built from simple services
```

### Performance & Caching

Services are the perfect place for performance optimizations:

```python
class MovementService:
    def __init__(self, game_state):
        self.game_state = game_state
        self._pathfinding_cache = {}  # Cache expensive calculations
        self._accessibility_cache = {}
    
    def get_movement_options(self, unit_id):
        # Cache results, invalidate when game state changes
        if unit_id in self._accessibility_cache:
            return self._accessibility_cache[unit_id]
```

## Framework Pattern: Domain-Driven Design

The service structure follows **Domain-Driven Design (DDD)** principles with clear layered architecture:

### Layered Architecture:
```
Presentation Layer    → Flask API endpoints
Application Layer     → Services (coordinate use cases)  
Domain Layer         → Abilities, Entities (core game rules)
Infrastructure Layer → GameState, persistence
```

### Service Types:
1. **Application Services** (what we built): Coordinate domain operations for specific use cases
2. **Domain Services** (abilities): Implement core game rules  
3. **Infrastructure Services** (future): Database, external APIs

## Service Implementation Examples

### MovementService
- Handles all unit movement operations
- Validates fuel requirements
- Manages directional vs. inter-body movement
- Coordinates with exploration system

### CollectionService
- Resource gathering from spaces and structures
- Quantity validation and inventory management
- Multi-source collection support
- Permission and accessibility checking

### BuildingService
- Structure construction with resource validation
- Affordability checking and cost calculation
- Building requirements lookup
- Integration with ability system

### TimeService
- Centralized time advancement
- Entity lifecycle management
- Error-resilient time progression
- Coordinated state updates

### WorldBuilder
- Reusable world creation system
- Configurable generation parameters
- Clean initialization process
- Separation from application startup

## Benefits for Your Game

### Current Benefits:
- **Maintainable**: Business logic separated from web framework
- **Testable**: Can test game logic without HTTP overhead
- **Debuggable**: Clear error boundaries and validation points
- **Extensible**: Easy to add new operations or modify existing ones

### Future Capabilities Unlocked:
- **AI Players**: Services can be called by AI without going through HTTP
- **Game Replays**: Record service calls to recreate game states
- **Load Balancing**: Services can run on different servers
- **Real-time Multiplayer**: WebSocket handlers use same services as REST API
- **Mobile Apps**: Different UI, same business logic
- **Admin Tools**: Management interfaces use same validated operations

## Use Case Orchestration

Services implement **Use Cases** - complete user stories:

- **"As a player, I want to move my unit to explore new areas"** → `MovementService.move_unit()`
- **"As a player, I want to collect resources to build structures"** → `CollectionService.collect_resource()`  
- **"As a player, I want to build a factory to process materials"** → `BuildingService.build_structure()`

Each service method represents a **complete player intention**, not just a technical operation.

## Best Practices

### Service Design Principles

1. **Single Responsibility**: Each service handles one domain area
2. **Stateless Operations**: Services don't maintain state between calls
3. **Dependency Injection**: Services receive dependencies (GameState) in constructor
4. **Error Boundaries**: Services catch and translate domain errors to appropriate responses
5. **Validation First**: Always validate inputs before processing

### Error Handling Pattern

```python
class MovementService:
    def move_unit(self, player, unit_id, direction=None, target_space_id=None):
        try:
            # 1. Validate inputs
            unit = self._validate_unit(player, unit_id)
            
            # 2. Determine destination
            destination = self._calculate_destination(unit, direction, target_space_id)
            
            # 3. Execute operation
            result = self._perform_movement(player, unit, destination)
            
            return {"success": True, "result": result}
            
        except GameException as e:
            # Let global handler manage game-specific errors
            raise
        except Exception as e:
            # Wrap unexpected errors
            raise MovementException(f"Unexpected movement error: {str(e)}")
```

### Testing Strategy

```python
# Unit Tests - Test individual service methods
def test_movement_service_fuel_validation():
    game_state = create_test_game_state()
    service = MovementService(game_state)
    
    with pytest.raises(InsufficientFuelException):
        service.move_unit(player, unit_with_no_fuel, direction=0)

# Integration Tests - Test service interactions
def test_collect_and_build_workflow():
    # Test multiple services working together
    collection_result = collection_service.collect_resource(...)
    building_result = building_service.build_structure(...)
    assert building_result["success"]

# API Tests - Test through HTTP endpoints
def test_movement_api():
    response = client.post('/api/move_unit', json={...})
    assert response.status_code == 200
```

## Scaling Considerations

### Performance Optimization
- **Caching**: Add caching at service level for expensive operations
- **Batch Operations**: Implement batch methods for multiple operations
- **Async Processing**: Services can be made async for I/O operations

### Horizontal Scaling
- **Stateless Design**: Services can run on multiple servers
- **Event Sourcing**: Record service calls for replay and debugging
- **Microservices**: Services can be extracted to separate applications

### Monitoring & Observability
- **Metrics**: Add performance metrics to service methods
- **Logging**: Structured logging for service operations
- **Health Checks**: Service health endpoints for monitoring

## Conclusion

The Service Layer architecture transforms your game from a prototype into a professional, scalable platform. It provides:

- **Clear separation of concerns** between API, business logic, and data
- **Testable, maintainable code** that can evolve with your game
- **Foundation for advanced features** like AI, multiplayer, and mobile support
- **Professional development patterns** used in production game systems

Services aren't just "helper layers" - they're the **architectural foundation** that enables serious game development and positions your project for long-term success.

By implementing this pattern, you've built a system that can grow from a single-player web game to a full-featured game platform while maintaining code quality and developer productivity.