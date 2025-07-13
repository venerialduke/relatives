"""
Main Flask application with modular service architecture.
Clean separation of concerns with proper error handling.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS

# Core imports
from core.game_state import GameState

# Service imports
from services.world_builder import WorldBuilder
from services.movement_service import MovementService
from services.collection_service import CollectionService
from services.building_service import BuildingService
from services.time_service import TimeService

# Utility imports
from utils.entity_utils import find_player_units, get_movement_destinations_for_unit, calculate_movement_cost_for_unit

# Exception imports
from exceptions.game_exceptions import (
    GameException, MovementException, CollectionException, 
    BuildingException, EntityNotFoundException
)

# Configuration
from config.game_config import FUEL_ID

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize game state and services
game_state = GameState()
world_builder = WorldBuilder(game_state)
movement_service = MovementService(game_state)
collection_service = CollectionService(game_state)
building_service = BuildingService(game_state)
time_service = TimeService(game_state)

# Build the default world
system, player, player_unit = world_builder.build_default_world()

# Global error handler
@app.errorhandler(GameException)
def handle_game_exception(e):
    """Handle all game-related exceptions with proper HTTP status codes."""
    status_code = 400
    if isinstance(e, EntityNotFoundException):
        status_code = 404
    elif isinstance(e, (MovementException, CollectionException, BuildingException)):
        status_code = 400
    
    return jsonify({"error": str(e)}), status_code

# Core game state endpoints
@app.route('/api/system')
def get_system():
    """Get complete system information."""
    try:
        return jsonify(system.to_dict_details(game_state=game_state))
    except Exception as e:
        return jsonify({"error": f"Failed to get system: {str(e)}"}), 500

@app.route('/api/game_state')
def get_game_state():
    """Get complete game state."""
    try:
        return jsonify(game_state.to_dict())
    except Exception as e:
        return jsonify({"error": f"Failed to get game state: {str(e)}"}), 500

@app.route("/api/player_units/<player_id>")
def api_find_player_units(player_id):
    """Get all units owned by a player."""
    try:
        units = find_player_units(game_state, player_id)
        return jsonify(units)
    except Exception as e:
        return jsonify({"error": f"Failed to get player units: {str(e)}"}), 500

@app.route('/api/unit')
def get_unit():
    """Get unit information by ID or name."""
    unit_id = request.args.get("unit_id")
    unit_name = request.args.get("unit_name")

    try:
        from utils.entity_utils import find_unit
        unit = find_unit(game_state, unit_id=unit_id, unit_name=unit_name)
        if unit:
            return jsonify(unit.to_dict())
        return jsonify({"error": "Unit not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to get unit: {str(e)}"}), 500

# Movement endpoints
@app.route('/api/move_unit', methods=['POST'])
def move_unit():
    """Move a unit by direction or to specific space."""
    try:
        data = request.json
        unit_id = data.get("unit_id")
        direction = data.get("direction")
        target_space_id = data.get("space_id")

        if not unit_id:
            return jsonify({"error": "Missing unit_id"}), 400

        result = movement_service.move_unit(
            player=player,
            unit_id=unit_id,
            direction=direction,
            target_space_id=target_space_id
        )
        
        return jsonify(result)
    
    except GameException:
        raise  # Re-raise to be handled by error handler
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route('/api/movement_destinations', methods=['GET'])
def get_movement_destinations():
    """Get available movement destinations for a unit."""
    unit_id = request.args.get("unit_id")
    
    if not unit_id:
        return jsonify({"error": "Missing unit_id"}), 400
    
    try:
        destinations = get_movement_destinations_for_unit(game_state, unit_id)
        if "error" in destinations and destinations["error"] is not None:
            return jsonify(destinations), 400
        return jsonify(destinations)
    except Exception as e:
        return jsonify({"error": f"Failed to get movement destinations: {str(e)}"}), 500

@app.route('/api/movement_cost', methods=['GET'])
def get_movement_cost():
    """Calculate movement cost for a specific destination."""
    unit_id = request.args.get("unit_id")
    target_space_id = request.args.get("target_space_id")
    
    if not unit_id:
        return jsonify({"error": "Missing unit_id"}), 400
    if not target_space_id:
        return jsonify({"error": "Missing target_space_id"}), 400
    
    try:
        cost_info = calculate_movement_cost_for_unit(game_state, unit_id, target_space_id)
        
        if "error" in cost_info and cost_info["error"] is not None:
            return jsonify(cost_info), 400
            
        return jsonify(cost_info)
    except Exception as e:
        return jsonify({"error": f"Failed to calculate movement cost: {str(e)}"}), 500

# Collection endpoints
@app.route('/api/collect_item', methods=['POST'])
def collect_item():
    """Collect resources from spaces or structures."""
    try:
        data = request.json
        unit_id = data.get("unit_id")
        resource_input = data.get("resource_id")
        quantity = data.get("quantity")
        space_id = data.get("space_id")
        structure_id = data.get("structure_id")

        if not unit_id:
            return jsonify({"error": "Missing unit_id"}), 400
        if not resource_input:
            return jsonify({"error": "Missing resource_id"}), 400

        result = collection_service.collect_resource(
            player=player,
            unit_id=unit_id,
            resource_input=resource_input,
            quantity=quantity,
            space_id=space_id,
            structure_id=structure_id
        )
        
        return jsonify(result)
    
    except GameException:
        raise  # Re-raise to be handled by error handler
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

# Building endpoints
@app.route('/api/build_structure', methods=['POST'])
def build_structure():
    """Build a structure at unit's location."""
    try:
        data = request.json
        structure_type = data.get("structure_type")
        unit_id = data.get("unit_id")

        if not unit_id:
            return jsonify({"error": "Missing unit_id"}), 400
        if not structure_type:
            return jsonify({"error": "Missing structure_type"}), 400

        result = building_service.build_structure(
            player=player,
            unit_id=unit_id,
            structure_type=structure_type
        )
        
        return jsonify(result)
    
    except GameException:
        raise  # Re-raise to be handled by error handler
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route('/api/building_requirements/<structure_type>')
def get_building_requirements(structure_type):
    """Get resource requirements for a structure type."""
    try:
        requirements = building_service.get_building_requirements(structure_type)
        return jsonify(requirements)
    except Exception as e:
        return jsonify({"error": f"Failed to get requirements: {str(e)}"}), 500

@app.route('/api/can_afford/<unit_id>/<structure_type>')
def can_afford_structure(unit_id, structure_type):
    """Check if unit can afford to build a structure."""
    try:
        result = building_service.can_afford_structure(unit_id, structure_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Failed to check affordability: {str(e)}"}), 500

# Time management endpoints
@app.route('/api/advance_time', methods=['POST'])
def advance_time():
    """Advance game time by one tick."""
    try:
        result = time_service.advance_time()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Failed to advance time: {str(e)}"}), 500

@app.route('/api/current_time')
def get_current_time():
    """Get current game time."""
    try:
        return jsonify({"time": time_service.get_current_time()})
    except Exception as e:
        return jsonify({"error": f"Failed to get time: {str(e)}"}), 500

# Space Port endpoints
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

@app.route('/api/space_ports')
def get_all_space_ports():
    """Get information about all Space Ports."""
    try:
        from services.space_port_service import SpacePortService
        space_port_service = SpacePortService(game_state)
        ports = space_port_service.get_all_space_ports()
        
        return jsonify({
            "space_ports": [port.to_dict(game_state) for port in ports],
            "total_count": len(ports)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Health check endpoint
@app.route('/api/health')
def health_check():
    """API health check endpoint."""
    return jsonify({
        "status": "healthy",
        "services": {
            "game_state": len(game_state.units) > 0,
            "world_builder": system is not None,
            "player": player is not None
        }
    })

if __name__ == '__main__':
    app.run(debug=True)