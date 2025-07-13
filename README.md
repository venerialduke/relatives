# Relatives - Resource Management Extraction Game

## Overview

Relatives is a beat-the-clock resource management extraction game where players make strategic decisions about exploration, resource extraction, and construction to achieve objectives before time runs out. The game features a hexagonal grid-based world with multiple celestial bodies, each containing spaces rich with various resources.

## Game Concept

### Current Game Mode
The current implementation focuses on a single "map" or "level" featuring:
- **Objective**: Efficiently explore, extract resources, and build structures before time expires
- **Resource Management**: 23+ different resource types including Iron, Crystal, Gas, Ice, Silver, Algae, and more
- **Exploration System**: Fog of war mechanics with gradual world discovery
- **Construction**: Five structure types with distinct functions and resource requirements
- **Movement**: Fuel-based travel system with local and inter-body movement

### Future Vision
- **Recipe Creation**: Players will discover and create new recipes for structures, units, and abilities
- **Resource Discovery**: Truly unique resources can be discovered (not just predefined ones)
- **Modular Expansion**: Multiple game modes and maps
- **Emergent Gameplay**: Deep systems that support player creativity and strategy

## Technical Architecture

### Backend (Python/Flask)
The backend follows a modular, object-oriented design with clear separation of concerns:

#### Core Components
- **Containers**: Spatial hierarchy (System → Body → Space)
  - `System`: Star systems containing multiple bodies
  - `Body`: Planets, asteroids, moons with individual spaces
  - `Space`: Individual hexagonal tiles with inventories and structures

- **Entities**: Game actors with abilities and inventories
  - `Unit`: Player-controlled entities (PlayerUnit)
  - `Structure`: Buildings with specialized functions (Collector, Factory, Settlement, FuelPump, Scanner)
  - `Resource`: Game materials with properties

- **Abilities**: Modular action system
  - `MoveAbility`: Handles local and inter-body movement
  - `CollectAbility`: Resource gathering from spaces and structures
  - `BuildAbility`: Structure construction with resource validation

- **Game Monitors**: Central state management
  - `GameState`: Global registry for all game objects
  - Time advancement system for all entities

- **Game Owners**: Player and ownership system
  - `Player`: Manages unit ownership and ability execution
  - Permission system for entity control

#### Key Systems
- **Spatial System**: Hexagonal coordinate system with efficient pathfinding
- **Inventory System**: Resource storage and management across all entities
- **Fuel Economy**: Movement costs with resource consumption
- **Exploration**: Progressive world discovery with accessibility tracking
- **Time Management**: Turn-based advancement with entity-specific behaviors

### Frontend (React/Vite)
Modern React application with intuitive user interface:

#### Component Architecture
- **GameView**: Main game controller with state management and keyboard controls
- **MapView**: SVG-based hexagonal grid with zoom/pan capabilities
- **Sidebar**: Control panel for resource management and actions
- **ResourceCollector**: Multi-source resource gathering interface
- **StructureBuilder**: Construction system with cost validation
- **LongDistanceMove**: Inter-body travel management

#### Features
- **Responsive Design**: Split-screen layout optimized for gameplay
- **Interactive Map**: Mouse wheel zoom, right-click pan, fog of war
- **Visual Feedback**: Resource highlighting, structure visualization, directional indicators
- **Real-time Updates**: Immediate UI feedback with backend synchronization
- **Space Theme**: Dark UI with Hubble telescope imagery and stellar backgrounds

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

The game will be available at `http://localhost:5173` with the backend API running on `http://localhost:5000`.

## Game Controls

### Keyboard Controls
- **Arrow Keys**: Rotate player unit direction
- **Enter**: Move forward in current direction
- **Space**: Open long-distance movement options

### Mouse Controls
- **Mouse Wheel**: Zoom in/out on map
- **Right-click + Drag**: Pan around the map
- **Left-click**: Select spaces, resources, and interface elements

## Current Features

### Resource Management
- **23 Resource Types**: Iron, Crystal, Gas, Ice, Silver, Algae, Silicon, Copper, Sand, Carbon, Nickel, Stone, Obsidian, Quartz, Dust, Water, Oil, Fish, Plasma, Fungus, Xenonite, Ore, SpaceDust
- **Fuel Economy**: Special fuel resource required for movement
- **Inventory System**: Track resources across units, structures, and spaces
- **Collection System**: Gather resources from discovered spaces

### Exploration System
- **Fog of War**: Gradual world discovery as you explore
- **System-wide Access**: Certain spaces always visible for navigation
- **Unit Exploration**: Individual units track their discovered areas
- **Visual Indicators**: Different opacity levels for exploration states

### Construction System
- **5 Structure Types**:
  - **Collector**: Automated resource harvesting (Cost: 2 Silver, 1 Ore)
  - **Factory**: Material processing (Cost: 2 Algae, 3 SpaceDust)
  - **Settlement**: Population and research (Cost: 4 Fungus)
  - **FuelPump**: Fuel generation (Cost: 2 Ore, 1 Crystal)
  - **Scanner**: Enhanced exploration (Cost: 1 Ore, 1 Silicon)
- **Resource Requirements**: Real-time cost validation
- **Construction Validation**: Prevents building without sufficient resources

### Movement System
- **Local Movement**: Move between adjacent spaces on same body (1 fuel)
- **Inter-body Travel**: Jump between different celestial bodies (5 fuel)
- **Directional Facing**: Units have orientation affecting movement
- **Accessibility**: Only move to previously explored or system-accessible spaces

## Identified Improvement Opportunities

### Backend Optimizations
1. **Service Layer Pattern**: Extract business logic from Flask routes
2. **Repository Pattern**: Centralize data access patterns
3. **Configuration Management**: Move constants to dedicated config files
4. **Event System**: Implement proper event-driven architecture
5. **Spatial Indexing**: Optimize space lookups with spatial data structures
6. **State Persistence**: Add database layer for game state storage

### Frontend Enhancements
1. **State Management**: Implement Context API or Redux for centralized state
2. **API Layer**: Create dedicated service layer with error handling
3. **Component Optimization**: Split large components and add React.memo
4. **TypeScript Migration**: Add type safety for better development experience
5. **Testing**: Comprehensive unit and integration test coverage
6. **Performance**: Virtual scrolling and Canvas rendering for large maps

### Code Quality
1. **Type Safety**: Comprehensive type hints and runtime validation
2. **Error Handling**: Replace string-based errors with proper exception hierarchy
3. **Documentation**: Add comprehensive docstrings and architectural documentation
4. **Testing Infrastructure**: Unit tests, integration tests, and automated testing
5. **Dependency Management**: Resolve circular dependencies and improve imports

## Development Roadmap

### Short Term (Current Focus)
- [ ] Implement identified modularization improvements
- [ ] Add comprehensive error handling and validation
- [ ] Create unit and integration test suites
- [ ] Improve documentation and code comments
- [ ] Optimize spatial queries and inventory management

### Medium Term
- [ ] Add save/load functionality with persistence layer
- [ ] Implement advanced structure types and abilities
- [ ] Create balanced resource ecosystem and economy
- [ ] Add turn timer and win/lose conditions
- [ ] Enhance UI with animations and visual effects

### Long Term (Future Vision)
- [ ] Recipe creation and discovery system
- [ ] Procedural resource and ability generation
- [ ] Multiple game modes and map types
- [ ] Multiplayer functionality
- [ ] Advanced AI for automated units
- [ ] Comprehensive modding support

## Contributing

This project focuses on modularization and clean architecture. When contributing:

1. Follow the existing architectural patterns
2. Add comprehensive tests for new functionality
3. Update documentation for any API changes
4. Consider performance implications of spatial operations
5. Maintain the separation between frontend and backend concerns

## License

[Specify your license here]

## Credits

- Hubble Space Telescope imagery used for space backgrounds
- React and Flask communities for excellent frameworks
- Contributors and testers who provide feedback and improvements