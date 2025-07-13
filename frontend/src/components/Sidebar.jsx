
import React, { useState } from "react";
import ResourceList from "./ResourceList";
import ResourceCollector from "./ResourceCollector";
import StructureBuilder from "./StructureBuilder";
import LongDistanceMove from "./LongDistanceMove";

function Sidebar({ system, playerUnits, refreshState }) {
  const [showLongDistanceMove, setShowLongDistanceMove] = useState(false);
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

  // Check if player has enough fuel for inter-body movement
  const currentFuel = unitInventory?.Fuel || 0;
  const canAffordLongDistance = currentFuel >= 5;

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
      
      <div className="movement-controls">
        <button 
          onClick={() => setShowLongDistanceMove(true)}
          className={`long-distance-button ${canAffordLongDistance ? 'affordable' : 'unaffordable'}`}
          disabled={!canAffordLongDistance}
          title={canAffordLongDistance ? 'Travel to other bodies (5 fuel)' : 'Need 5 fuel for inter-body travel'}
        >
          Long Distance Move {canAffordLongDistance ? '' : '(Need 5 fuel)'}
        </button>
      </div>

      <button onClick={() => {
        fetch("/api/advance_time", { method: "POST" })
          .then(res => res.json())
          .then(() => refreshState());  // or call a `refreshState()` if passed down
      }}>
        Next Turn
      </button>

      <LongDistanceMove
        playerUnit={playerUnit}
        isVisible={showLongDistanceMove}
        onClose={() => setShowLongDistanceMove(false)}
        onMoveComplete={() => {
          refreshState();
          setShowLongDistanceMove(false);
        }}
      />
    </div>
  );
}

export default Sidebar;