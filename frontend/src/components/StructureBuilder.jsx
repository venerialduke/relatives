import React, { useState } from "react";

const STRUCTURE_REQUIREMENTS = {
  "Collector": {"Silver": 2, "Ore": 1},
  "Factory": {"Algae": 2, "SpaceDust": 3},
  "Settlement": {"Fungus": 4},
  "FuelPump": {"Ore": 2, "Crystal": 1},
  "Scanner": {"Ore": 1, "Silicon": 1},
  "SpacePort": {"Silicon": 3, "Crystal": 2, "Ore": 2, "SpaceDust": 1}
};

const STRUCTURE_DESCRIPTIONS = {
  "Collector": "Automatically harvests resources from nearby spaces",
  "Factory": "Processes raw materials into advanced components", 
  "Settlement": "Houses population and provides research bonuses",
  "FuelPump": "Generates 1 fuel per turn for unit movement",
  "Scanner": "Reveals hidden resources and distant spaces",
  "SpacePort": "Enables reduced-cost travel to other Space Ports (2 fuel vs 5)"
};

function StructureBuilder({ playerUnit, refreshState }) {
  const [isBuilding, setIsBuilding] = useState(false);
  const [message, setMessage] = useState("");
  const [buildingStructure, setBuildingStructure] = useState("");

  if (!playerUnit || !playerUnit.named_inventory) {
    return null;
  }

  const playerInventory = playerUnit.named_inventory;

  const canAfford = (requirements) => {
    return Object.entries(requirements).every(([resource, needed]) => {
      const available = playerInventory[resource] || 0;
      return available >= needed;
    });
  };

  const getMissingResources = (requirements) => {
    const missing = [];
    Object.entries(requirements).forEach(([resource, needed]) => {
      const available = playerInventory[resource] || 0;
      if (available < needed) {
        missing.push(`${resource} (${needed - available})`);
      }
    });
    return missing;
  };

  const handleBuild = async (structureType) => {
    if (!canAfford(STRUCTURE_REQUIREMENTS[structureType])) {
      setMessage(`Cannot build ${structureType}: insufficient resources`);
      return;
    }

    setIsBuilding(true);
    setBuildingStructure(structureType);
    setMessage("");

    try {
      const response = await fetch("/api/build_structure", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          unit_id: playerUnit.id,
          structure_type: structureType
        })
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(`✓ ${data.result}`);
        if (refreshState) {
          refreshState();
        }
      } else {
        setMessage(`Error: ${data.error || "Build failed"}`);
      }
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setIsBuilding(false);
      setBuildingStructure("");
    }
  };

  return (
    <div className="structure-builder">
      <h4>Build Structures</h4>
      
      <div className="structure-list">
        {Object.entries(STRUCTURE_REQUIREMENTS).map(([structureType, requirements]) => {
          const affordable = canAfford(requirements);
          const missing = getMissingResources(requirements);
          const currentlyBuilding = isBuilding && buildingStructure === structureType;

          return (
            <div key={structureType} className={`structure-card ${affordable ? 'affordable' : 'unaffordable'}`}>
              <div className="structure-header">
                <h5>{structureType}</h5>
                <span className={`status ${affordable ? 'can-build' : 'cannot-build'}`}>
                  {affordable ? '✓ Can Build' : '❌ Missing'}
                </span>
              </div>
              
              <div className="structure-description">
                {STRUCTURE_DESCRIPTIONS[structureType]}
              </div>

              <div className="structure-cost">
                <strong>Cost:</strong> {Object.entries(requirements).map(([resource, amount], index) => (
                  <span key={resource} className={`cost-item ${(playerInventory[resource] || 0) >= amount ? 'sufficient' : 'insufficient'}`}>
                    {index > 0 && ', '}
                    {resource} ({amount})
                  </span>
                ))}
              </div>

              {!affordable && missing.length > 0 && (
                <div className="missing-resources">
                  <strong>Need:</strong> {missing.join(', ')}
                </div>
              )}

              <button 
                onClick={() => handleBuild(structureType)}
                disabled={!affordable || isBuilding}
                className="build-button"
              >
                {currentlyBuilding ? "Building..." : "Build"}
              </button>
            </div>
          );
        })}
      </div>

      {message && (
        <div className={`build-message ${message.startsWith('✓') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}
    </div>
  );
}

export default StructureBuilder;