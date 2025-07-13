# Common Issues Documentation

## Overview
This document catalogs common issues encountered during development and testing of the Relatives game project. It serves as a reference for troubleshooting and avoiding recurring problems.

## Testing and Development Issues

### Import and Module Issues

#### 1. **Missing Flask Module in Virtual Environment**
**Issue**: `ModuleNotFoundError: No module named 'flask'` when testing imports
```bash
python -c "import app; print('Backend imports successfully')"
# Error: ModuleNotFoundError: No module named 'flask'
```

**Cause**: Virtual environment not activated or dependencies not installed

**Solutions**:
- Activate virtual environment first: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
- Install dependencies: `pip install -r requirements.txt`
- For testing without Flask, test specific modules instead of full app

**Testing Workaround**:
```bash
# Instead of testing full app import
python -c "from config.game_config import SPACE_PORT_TRAVEL_COST; print('Config works')"
```

#### 2. **Unicode Character Display Issues on Windows**
**Issue**: `UnicodeEncodeError: 'charmap' codec can't encode character` when using emoji in print statements
```python
print('✅ Success')  # Fails on Windows terminal
```

**Cause**: Windows terminal encoding limitations

**Solutions**:
- Use plain text instead of Unicode characters in test scripts
- Set environment variable: `set PYTHONIOENCODING=utf-8`
- Use ASCII alternatives: `SUCCESS:` instead of `✅`

**Safe Testing Pattern**:
```python
try:
    # Test code
    print('SUCCESS: Feature works')
except Exception as e:
    print(f'ERROR: {e}')
```

### Structure Implementation Issues

#### 3. **Inconsistent Structure Constructor Patterns**
**Issue**: `TypeError: SpacePort.__init__() missing 1 required positional argument: 'name'`

**Cause**: Mixed use of dataclasses vs regular classes in structure definitions

**Problem**: SpacePort was initially implemented as `@dataclass` but other structures use regular classes with explicit `__init__`

**Solution**: Match existing structure patterns exactly
```python
# Wrong: @dataclass approach
@dataclass
class SpacePort(Structure):
    is_operational: bool = True

# Correct: Regular class matching existing patterns
class SpacePort(Structure):
    def __init__(self, id: str, location_space_id: str):
        super().__init__(id=id, name="Space Port", location_space_id=location_space_id)
        self.is_operational = True
```

**Prevention**: Always check existing structure patterns in `structure_map.py` before implementing new structures

#### 4. **Service Circular Import Issues**
**Issue**: Importing services within utility functions can cause circular imports

**Example Problem**:
```python
# In utils/entity_utils.py
def get_movement_options_for_unit(game_state, unit_id):
    from services.space_port_service import SpacePortService  # Can cause issues
```

**Solutions**:
- Import at module level when possible
- Use late imports only when necessary
- Consider dependency injection patterns
- Move shared functionality to appropriate service layers

### Configuration and Constants Issues

#### 5. **Missing Configuration Constants**
**Issue**: Using hardcoded values instead of centralized configuration

**Example**:
```python
# Wrong: Hardcoded values
if current_fuel < 5:  # Magic number

# Correct: Use configuration
from config.game_config import INTER_BODY_FUEL_COST
if current_fuel < INTER_BODY_FUEL_COST:
```

**Prevention**: Always add new constants to `config/game_config.py` and import them

#### 6. **Inconsistent Fuel ID References**
**Issue**: Multiple definitions of `FUEL_ID` across different files

**Problem**: Can lead to inconsistencies and maintenance issues

**Solution**: Use single source of truth in `config/game_config.py`
```python
# config/game_config.py
FUEL_ID = 'fuel'

# All other files
from config.game_config import FUEL_ID
```

### Testing Strategy Issues

#### 7. **Complex Integration Testing Without Setup**
**Issue**: Testing complex integrations without proper game state setup

**Problem**: Features require initialized game state, players, units, etc.

**Solution**: Create minimal test setups
```python
# Good testing pattern
game_state = GameState()
service = SomeService(game_state)
# Test specific service functionality

# Avoid testing full app integration without proper setup
```

#### 8. **Incomplete Error Handling in Tests**
**Issue**: Tests fail silently or with unclear error messages

**Solution**: Always include exception handling and traceback in test scripts
```python
try:
    # Test code
    print('SUCCESS: Test passed')
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
```

## Architecture and Design Issues

### Service Layer Issues

#### 9. **Service Dependencies Not Injected**
**Issue**: Services creating their own dependencies instead of receiving them

**Problem**: Makes testing difficult and creates tight coupling

**Example**:
```python
# Wrong: Service creates its own dependencies
class MovementService:
    def __init__(self, game_state):
        self.space_port_service = SpacePortService(game_state)  # Tight coupling

# Better: Dependency injection (for future)
class MovementService:
    def __init__(self, game_state, space_port_service=None):
        self.space_port_service = space_port_service or SpacePortService(game_state)
```

#### 10. **Mixing Business Logic in Utility Functions**
**Issue**: Complex business logic in utility functions instead of services

**Solution**: Move complex logic to appropriate services, keep utilities simple

### API and Endpoint Issues

#### 11. **Missing Error Handling in API Endpoints**
**Issue**: API endpoints that don't handle service exceptions properly

**Pattern**: Always wrap service calls in try-catch blocks
```python
@app.route('/api/some_endpoint')
def some_endpoint():
    try:
        result = some_service.do_something()
        return jsonify(result)
    except GameException:
        raise  # Let global handler manage
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
```

## Prevention Strategies

### Before Implementing New Features

1. **Check Existing Patterns**: Review how similar features are implemented
2. **Update Configuration**: Add any new constants to centralized config
3. **Plan Service Integration**: Determine which services need enhancement
4. **Design Error Handling**: Plan exception types and error responses

### Testing Checklist

1. **Basic Import Test**: Verify all new modules import correctly
2. **Constructor Test**: Verify new classes can be instantiated
3. **Integration Test**: Test service interactions with minimal setup
4. **Configuration Test**: Verify constants are accessible and correct
5. **Error Path Test**: Test error conditions and exception handling

### Code Review Points

1. **No Magic Numbers**: All constants in centralized configuration
2. **Consistent Patterns**: Follow existing architectural patterns
3. **Proper Error Handling**: Use exception hierarchy, not string returns
4. **Clean Dependencies**: Minimize circular imports and tight coupling
5. **Unicode Safety**: Avoid Unicode characters in test output

#### 12. **Movement Service Debugging**
**Issue**: Long distance movement failing with fuel cost errors despite sufficient fuel

**Debugging Approach**: Add temporary debug logging to movement service
```python
# In _handle_direct_movement method
print(f"DEBUG: Movement {current_space.id} -> {target_space_id}")
print(f"DEBUG: Space Port travel: {is_space_port_travel}, Required: {required_fuel}, Have: {current_fuel}")
```

**Common Causes**:
- Space Port detection logic incorrectly identifying regular movement as Space Port travel
- Fuel cost constants not properly imported
- Unit inventory not properly tracking fuel
- Movement service changes affecting existing logic

**Solution Pattern**: Temporarily add logging, test movement, identify issue, fix root cause, remove logging

## Future Issue Categories

### Performance Issues
*To be documented as performance testing is implemented*

### Database Integration Issues  
*To be documented when persistence layer is added*

### Frontend Integration Issues
*To be documented as frontend features are tested*

### Multiplayer and Concurrency Issues
*To be documented when multiplayer features are implemented*

---

## How to Use This Document

1. **When Encountering an Issue**: Check if it's documented here first
2. **When Resolving New Issues**: Add them to this document with solutions
3. **Before Starting Development**: Review relevant sections for prevention strategies
4. **During Code Review**: Use checklist items to catch common problems

This document should be updated whenever new common issues are discovered or existing solutions are improved.