
import React, { useState } from "react";
import ResourceList from "./ResourceList";
import ResourceCollector from "./ResourceCollector";
import StructureBuilder from "./StructureBuilder";
import UnitManager from "./UnitManager";

function Sidebar({ system, playerUnits, refreshState }) {
  const [unitManagerVisible, setUnitManagerVisible] = useState(false);
  const playerUnit = playerUnits?.[0];
  const currentSpaceId = playerUnit?.location_space_id;
  const unitInventory = playerUnit?.named_inventory;

  let currentSpace = null;
  let bodyName = null;
  let spaceIndex = null;

  if (system && currentSpaceId) {
    for (const body of system.bodies) {
      const index = body.spaces.findIndex(s => s.id === currentSpaceId);
      if (index !== -1) {
        currentSpace = body.spaces[index];
        bodyName = body.name;
        spaceIndex = index + 1;
        break;
      }
    }
  }

  // Always allow long distance move - let the UI handle specific costs
  const currentFuel = unitInventory?.Fuel || 0;

  return (
    <div className="sidebar">
      <h2>Info Panel</h2>
      {currentSpace ? (
        <>
          <h3>Current Space</h3>
          <p><strong>Location:</strong> {bodyName} – Space {spaceIndex}</p>
          <p><strong>Coordinates:</strong> ({currentSpace.q}, {currentSpace.r})</p>

          <ResourceList title="Resources on Space" resources={currentSpace.named_inventory} />
          <ResourceCollector 
            currentSpace={currentSpace} 
            playerUnit={playerUnit} 
            refreshState={refreshState} 
          />
          <StructureBuilder 
            playerUnit={playerUnit} 
            refreshState={refreshState} 
          />
          <ResourceList title="Unit Inventory" resources={unitInventory} />
        </>
      ) : (
        <p>No unit or space selected.</p>
      )}

      <hr />
      
      <div className="movement-help">
        <p style={{ fontSize: '14px', color: '#666', margin: '8px 0' }}>
          💡 <strong>Tip:</strong> Right-click or Shift+click on any explored space to move there!
        </p>
      </div>

      <button onClick={() => {
        fetch("/api/advance_time", { method: "POST" })
          .then(res => res.json())
          .then(() => refreshState());  // or call a `refreshState()` if passed down
      }}>
        Next Turn
      </button>

      <button 
        onClick={() => setUnitManagerVisible(true)}
        className="autonomous-unit-manager-btn"
        style={{
          marginTop: '10px',
          backgroundColor: '#9C27B0',
          color: 'white',
          border: 'none',
          padding: '8px 12px',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        🤖 Manage Autonomous Units
      </button>

      <UnitManager
        isVisible={unitManagerVisible}
        onClose={() => setUnitManagerVisible(false)}
        refreshState={refreshState}
      />

    </div>
  );
}

export default Sidebar;