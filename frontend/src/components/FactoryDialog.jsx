import React, { useState, useEffect } from "react";

const MINING_DRONE_DESCRIPTION = "Autonomous unit that searches for resources, collects them, and delivers to collection structures. Operates independently for 30 turns.";

function FactoryDialog({ factory, onClose, refreshState }) {
  const [factoryStatus, setFactoryStatus] = useState(null);
  const [unitCosts, setUnitCosts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [building, setBuilding] = useState(false);
  const [message, setMessage] = useState("");
  const [selectedUnitType, setSelectedUnitType] = useState("mining_drone");
  const [targetResource, setTargetResource] = useState("iron");

  useEffect(() => {
    if (factory) {
      loadFactoryData();
    }
  }, [factory]);

  const loadFactoryData = async () => {
    try {
      setLoading(true);
      const [statusResponse, costsResponse] = await Promise.all([
        fetch(`http://localhost:5000/api/factory_status/${factory.id}`),
        fetch(`http://localhost:5000/api/unit_build_costs/mining_drone`)
      ]);

      if (statusResponse.ok && costsResponse.ok) {
        const status = await statusResponse.json();
        const costs = await costsResponse.json();
        setFactoryStatus(status);
        setUnitCosts(costs);
      } else {
        setMessage("Failed to load factory information");
      }
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleBuildUnit = async () => {
    if (!factoryStatus || building) return;

    try {
      setBuilding(true);
      setMessage("");

      const response = await fetch('http://localhost:5000/api/build_unit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          factory_id: factory.id,
          unit_type: selectedUnitType,
          target_resource: targetResource
        }),
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setMessage(`✓ ${result.message}`);
        // Refresh factory status
        await loadFactoryData();
        // Refresh main game state
        if (refreshState) {
          refreshState();
        }
      } else {
        setMessage(`✗ ${result.error || 'Failed to build unit'}`);
      }
    } catch (error) {
      setMessage(`✗ Error: ${error.message}`);
    } finally {
      setBuilding(false);
    }
  };

  const canAfford = (costs) => {
    if (!factoryStatus || !costs) return false;
    
    return Object.entries(costs).every(([resource, needed]) => {
      const available = factoryStatus.inventory[resource] || 0;
      return available >= needed;
    });
  };

  const getMissingResources = (costs) => {
    if (!factoryStatus || !costs) return [];
    
    const missing = [];
    Object.entries(costs).forEach(([resource, needed]) => {
      const available = factoryStatus.inventory[resource] || 0;
      if (available < needed) {
        missing.push(`${resource} (need ${needed - available} more)`);
      }
    });
    return missing;
  };

  const formatCooldownStatus = () => {
    if (!factoryStatus) return "";
    
    if (factoryStatus.build_status.can_build_this_turn) {
      return "✓ Ready to build";
    } else {
      const cooldown = factoryStatus.build_status.build_cooldown;
      return `⏳ Cooldown: ${cooldown} turn${cooldown !== 1 ? 's' : ''} remaining`;
    }
  };

  if (!factory) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center" style={{ zIndex: 10000 }}>
      <div className="bg-gray-900 text-white rounded-lg p-6 max-w-md w-full mx-4 max-h-96 overflow-y-auto border border-gray-700 shadow-2xl">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Factory Control</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-xl"
          >
            ×
          </button>
        </div>

        {loading ? (
          <div className="text-center py-4">Loading factory data...</div>
        ) : (
          <>
            {/* Factory Status */}
            <div className="mb-4 p-3 bg-gray-700 rounded">
              <h3 className="font-semibold mb-2">Factory Status</h3>
              <div className="text-sm space-y-1">
                <div>{formatCooldownStatus()}</div>
                <div>Location: {factoryStatus?.location}</div>
                <div className="mt-2">
                  <strong>Inventory:</strong>
                  <div className="grid grid-cols-2 gap-1 mt-1">
                    {factoryStatus && Object.entries(factoryStatus.inventory)
                      .filter(([_, amount]) => amount > 0)
                      .map(([resource, amount]) => (
                        <div key={resource} className="text-xs">
                          {resource}: {amount}
                        </div>
                      ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Unit Building Section */}
            <div className="mb-4">
              <h3 className="font-semibold mb-2">Build Autonomous Unit</h3>
              
              {/* Unit Type Selection */}
              <div className="mb-3">
                <label className="block text-sm font-medium mb-1">Unit Type:</label>
                <select
                  value={selectedUnitType}
                  onChange={(e) => setSelectedUnitType(e.target.value)}
                  className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-white"
                  disabled={building}
                >
                  <option value="mining_drone">Mining Drone</option>
                </select>
                <div className="text-xs text-gray-400 mt-1">
                  {MINING_DRONE_DESCRIPTION}
                </div>
              </div>

              {/* Target Resource Selection */}
              <div className="mb-3">
                <label className="block text-sm font-medium mb-1">Target Resource:</label>
                <select
                  value={targetResource}
                  onChange={(e) => setTargetResource(e.target.value)}
                  className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-white"
                  disabled={building}
                >
                  <option value="iron">Iron</option>
                  <option value="crystal">Crystal</option>
                  <option value="ore">Ore</option>
                  <option value="silicon">Silicon</option>
                </select>
              </div>

              {/* Build Costs */}
              {unitCosts && (
                <div className="mb-3 p-2 bg-gray-700 rounded">
                  <div className="text-sm font-medium mb-1">Build Costs:</div>
                  <div className="grid grid-cols-2 gap-1">
                    {Object.entries(unitCosts.costs).map(([resource, cost]) => (
                      <div key={resource} className="text-xs">
                        {resource}: {cost}
                      </div>
                    ))}
                  </div>
                  
                  {!canAfford(unitCosts.costs) && (
                    <div className="text-red-400 text-xs mt-2">
                      Missing: {getMissingResources(unitCosts.costs).join(", ")}
                    </div>
                  )}
                </div>
              )}

              {/* Build Button */}
              <button
                onClick={handleBuildUnit}
                disabled={
                  building || 
                  !factoryStatus?.build_status.can_build_this_turn ||
                  !canAfford(unitCosts?.costs)
                }
                className={`w-full p-2 rounded font-medium ${
                  building || 
                  !factoryStatus?.build_status.can_build_this_turn ||
                  !canAfford(unitCosts?.costs)
                    ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                    : 'bg-purple-600 hover:bg-purple-700 text-white'
                }`}
              >
                {building ? 'Building...' : 'Build Mining Drone'}
              </button>
            </div>

            {/* Status Message */}
            {message && (
              <div className={`p-2 rounded text-sm ${
                message.startsWith('✓') 
                  ? 'bg-green-800 text-green-200' 
                  : 'bg-red-800 text-red-200'
              }`}>
                {message}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default FactoryDialog;