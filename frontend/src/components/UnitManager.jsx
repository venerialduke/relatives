import React, { useState, useEffect } from "react";

function UnitManager({ isVisible, onClose, refreshState }) {
  const [autonomousUnits, setAutonomousUnits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statistics, setStatistics] = useState(null);
  const [selectedUnitId, setSelectedUnitId] = useState(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (isVisible) {
      loadUnitData();
    }
  }, [isVisible]);

  const loadUnitData = async () => {
    try {
      setLoading(true);
      
      // Load unit statistics
      const statsResponse = await fetch('http://localhost:5000/api/autonomous_units');
      
      // Load actual unit data from game state
      const gameStateResponse = await fetch('http://localhost:5000/api/game_state');
      
      if (statsResponse.ok && gameStateResponse.ok) {
        const stats = await statsResponse.json();
        const gameState = await gameStateResponse.json();
        
        const units = Object.values(gameState.autonomous_units || {});
        setAutonomousUnits(units);
        setStatistics(stats);
      } else {
        setMessage("Failed to load unit data");
      }
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getStateColor = (state) => {
    const colors = {
      search: "#FFA500",     // Orange
      collect: "#32CD32",    // Lime green
      deposit: "#4169E1",    // Royal blue
      returning: "#FFD700",  // Gold
      idle: "#808080",       // Gray
      expired: "#FF6B6B"     // Red
    };
    return colors[state] || "#808080";
  };

  const getStateIcon = (state) => {
    const icons = {
      search: "🔍",
      collect: "⛏️",
      deposit: "📦",
      returning: "↩️",
      idle: "⏸️",
      expired: "💀"
    };
    return icons[state] || "❓";
  };

  const getLifespanStatus = (lifespan) => {
    if (lifespan <= 5) return { color: "#FF6B6B", status: "Critical" };
    if (lifespan <= 10) return { color: "#FFA500", status: "Low" };
    if (lifespan <= 20) return { color: "#FFD700", status: "Medium" };
    return { color: "#32CD32", status: "High" };
  };

  const formatLocation = (locationId) => {
    // Extract meaningful parts from space ID like "body:body_4:0:0:1"
    const parts = locationId.split(':');
    if (parts.length >= 4) {
      const bodyName = parts[1].replace('body_', 'Body ');
      const coords = `(${parts[2]},${parts[3]})`;
      return `${bodyName} ${coords}`;
    }
    return locationId;
  };

  const handleUnitSelect = (unitId) => {
    setSelectedUnitId(selectedUnitId === unitId ? null : unitId);
  };

  const handleDismissUnit = async (unitId) => {
    // Future implementation: API endpoint to dismiss/recall units
    setMessage(`Dismiss functionality for ${unitId} coming soon`);
  };

  const getCargoInfo = (unit) => {
    if (!unit.inventory) return "No cargo";
    
    const cargo = Object.entries(unit.inventory)
      .filter(([resource, amount]) => resource !== 'fuel' && amount > 0)
      .map(([resource, amount]) => `${resource}: ${amount}`)
      .join(", ");
    
    return cargo || "Empty";
  };

  const getFuelLevel = (unit) => {
    return unit.inventory?.fuel || 0;
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
      <div className="bg-gray-900 text-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-96 overflow-y-auto border border-gray-700 shadow-2xl">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Autonomous Unit Manager</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-xl"
          >
            ×
          </button>
        </div>

        {loading ? (
          <div className="text-center py-4">Loading unit data...</div>
        ) : (
          <>
            {/* Statistics Overview */}
            {statistics && (
              <div className="mb-6 p-4 bg-gray-700 rounded">
                <h3 className="font-semibold mb-3">Fleet Overview</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <div className="text-gray-300">Total Units</div>
                    <div className="text-lg font-bold">{statistics.total_units}</div>
                  </div>
                  <div>
                    <div className="text-gray-300">Low Fuel</div>
                    <div className="text-lg font-bold text-orange-400">
                      {statistics.low_fuel_units?.length || 0}
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-300">Near Expiration</div>
                    <div className="text-lg font-bold text-red-400">
                      {statistics.near_expiration_units?.length || 0}
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-300">Average Lifespan</div>
                    <div className="text-lg font-bold">
                      {Math.round(statistics.average_lifespan || 0)}
                    </div>
                  </div>
                </div>

                {/* By State */}
                <div className="mt-4">
                  <div className="text-gray-300 mb-2">By State:</div>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(statistics.by_state || {}).map(([state, count]) => (
                      <span
                        key={state}
                        className="px-2 py-1 rounded text-xs"
                        style={{ backgroundColor: getStateColor(state) }}
                      >
                        {getStateIcon(state)} {state}: {count}
                      </span>
                    ))}
                  </div>
                </div>

                {/* By Type */}
                <div className="mt-4">
                  <div className="text-gray-300 mb-2">By Type:</div>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(statistics.by_type || {}).map(([type, count]) => (
                      <span
                        key={type}
                        className="px-2 py-1 bg-purple-600 rounded text-xs"
                      >
                        {type}: {count}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Unit List */}
            <div className="space-y-2">
              <h3 className="font-semibold mb-2">Individual Units ({autonomousUnits.length})</h3>
              
              {autonomousUnits.length === 0 ? (
                <div className="text-gray-400 text-center py-4">
                  No autonomous units deployed
                </div>
              ) : (
                autonomousUnits.map((unit) => {
                  const lifespanStatus = getLifespanStatus(unit.lifespan);
                  const isSelected = selectedUnitId === unit.id;
                  
                  return (
                    <div
                      key={unit.id}
                      className={`p-3 rounded cursor-pointer transition-colors ${
                        isSelected ? 'bg-gray-600' : 'bg-gray-700 hover:bg-gray-650'
                      }`}
                      onClick={() => handleUnitSelect(unit.id)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          {/* State indicator */}
                          <div
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: getStateColor(unit.state) }}
                            title={unit.state}
                          />
                          
                          {/* Unit info */}
                          <div>
                            <div className="font-medium">{unit.id}</div>
                            <div className="text-sm text-gray-300">
                              {getStateIcon(unit.state)} {unit.state} | 
                              Target: {unit.target_resource || 'Unknown'} | 
                              Location: {formatLocation(unit.location_space_id)}
                            </div>
                          </div>
                        </div>

                        <div className="text-right">
                          {/* Lifespan */}
                          <div 
                            className="text-sm font-medium"
                            style={{ color: lifespanStatus.color }}
                          >
                            {unit.lifespan} turns
                          </div>
                          <div className="text-xs text-gray-400">
                            {lifespanStatus.status}
                          </div>
                        </div>
                      </div>

                      {/* Expanded details */}
                      {isSelected && (
                        <div className="mt-3 pt-3 border-t border-gray-600">
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <strong>Fuel:</strong> {getFuelLevel(unit)}
                            </div>
                            <div>
                              <strong>Cargo:</strong> {getCargoInfo(unit)}
                            </div>
                            <div>
                              <strong>Home Base:</strong> {unit.home_collection_point || 'None'}
                            </div>
                            <div>
                              <strong>Type:</strong> {unit.unit_type || 'mining_drone'}
                            </div>
                          </div>

                          {/* Actions */}
                          <div className="mt-3 flex space-x-2">
                            <button
                              onClick={() => handleDismissUnit(unit.id)}
                              className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-xs"
                            >
                              Dismiss
                            </button>
                            <button
                              className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs"
                              title="Coming soon"
                              disabled
                            >
                              Recall
                            </button>
                            <button
                              className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-xs"
                              title="Coming soon"
                              disabled
                            >
                              Reprogram
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>

            {/* Status Message */}
            {message && (
              <div className="mt-4 p-2 bg-blue-800 text-blue-200 rounded text-sm">
                {message}
              </div>
            )}

            {/* Refresh Button */}
            <div className="mt-4 text-center">
              <button
                onClick={loadUnitData}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded"
              >
                Refresh Data
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default UnitManager;