
import React from "react";
import ResourceList from "./ResourceList";

function Sidebar({ system, playerUnits }) {
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

  return (
    <div className="sidebar">
      <h2>Info Panel</h2>
      {currentSpace ? (
        <>
          <h3>Current Space</h3>
          <p><strong>Location:</strong> {bodyName} – Space {spaceIndex}</p>
          <p><strong>Coordinates:</strong> ({currentSpace.q}, {currentSpace.r})</p>

          <ResourceList title="Resources on Space" resources={currentSpace.named_inventory} />
          <ResourceList title="Unit Inventory" resources={unitInventory} />
        </>
      ) : (
        <p>No unit or space selected.</p>
      )}

      <hr />
      <button onClick={() => {
        fetch("/api/advance_time", { method: "POST" })
          .then(res => res.json())
          .then(() => refreshState());  // or call a `refreshState()` if passed down
      }}>
        Next Turn
      </button>
    </div>
  );
}

export default Sidebar;