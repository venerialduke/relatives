import React from "react";

const Sidebar = ({
  unit,
  robots,
  deployingRobot,
  setDeployingRobot,
  turnTimer,
  advanceTime,
  selectedSpace,
  collectItem,
  buildBuilding,
  message,
  setMessage,
}) => {
  const summarizeInventory = (inventory) => {
    const summary = {};
    for (const item of inventory || []) {
      summary[item] = (summary[item] || 0) + 1;
    }
    return summary;
  };

  const canBuild = (buildingName, requirements) => {
    if (!unit || !unit.inventory) return false;
    const summary = summarizeInventory(unit.inventory);
    for (const [res, amount] of Object.entries(requirements)) {
      if ((summary[res] || 0) < amount) return false;
    }
    return true;
  };

  const inventorySummary = summarizeInventory(unit?.inventory);

  const buildOptions = {
    Collector: { Silver: 2, Ore: 1 },
    Factory: { Algae: 2, SpaceDust: 3 },
    Settlement: { Fungus: 4 },
    "Fuel Pump": { Ore: 2, Crystal: 1 },
    Scanner: { Ore: 1, Silicon: 1 },
  };

  return (
    <div className="sidebar">
      <h2>Inventory</h2>
      {deployingRobot && <p style={{ color: "purple" }}>Right-click a space to deploy a robot</p>}
      <button onClick={advanceTime}>Next Turn</button>
      <p>Next turn in: {turnTimer}s</p>

      {robots.length > 0 && (
        <div>
          <h3>Robots</h3>
          <ul>
            {robots.map((robot, i) => (
              <li key={i}>
                Robot {i}: {robot.mode} @ {robot.current_space_id}
              </li>
            ))}
          </ul>
        </div>
      )}

      <ul>
        {Object.entries(inventorySummary || {}).map(([item, count]) => (
          <li key={item}>
            {item} x{count}
            {item === "Robot" && count > 0 && (
              <button onClick={() => setDeployingRobot(true)}>Deploy</button>
            )}
          </li>
        ))}
      </ul>

      {selectedSpace && (
        <>
          <h2>{selectedSpace.name}</h2>
          {selectedSpace.building === "Factory" && selectedSpace.factory_robots > 0 && (
            <div>
              <p>Factory Robots: {selectedSpace.factory_robots}</p>
              <ul>
                {Array.from({ length: selectedSpace.factory_robots }).map((_, i) => (
                  <li key={i}>
                    Robot <button onClick={() => collectItem("Robot")}>Collect</button>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {selectedSpace.items?.length > 0 ? (
            <div>
              <p>Resources:</p>
              <ul>
                {selectedSpace.items.map((item, index) => (
                  <li key={`${item}-${index}`}>
                    {item} <button onClick={() => collectItem(item)}>Collect</button>
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <p>No items left</p>
          )}

          <h3>Build Options</h3>
          <ul>
            {Object.entries(buildOptions).map(([name, reqs]) => (
              <li key={name}>
                {name}{" "}
                {canBuild(name, reqs) && !selectedSpace.building ? (
                  <button onClick={() => buildBuilding(name)}>Build</button>
                ) : (
                  <span style={{ color: "gray" }}>
                    {selectedSpace.building
                      ? "Building already exists"
                      : ` (need: ${Object.entries(reqs)
                          .map(([res, amt]) => `${res} x${amt}`)
                          .join(", ")})`}
                  </span>
                )}
              </li>
            ))}
          </ul>
          <p>{message}</p>
        </>
      )}
    </div>
  );
};

export default Sidebar;