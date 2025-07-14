// GameView.jsx
import React, { useEffect, useState } from "react";
import MapView from "./MapView";
import Sidebar from "./Sidebar";
import { DIRECTION_ANGLES } from "./helpers";
import "./App.css";

function GameView() {
  const [system, setSystem] = useState(null);
  const [playerUnits, setPlayerUnits] = useState([]);
  const [unitDirection, setUnitDirection] = useState(0);
  const [zoom, setZoom] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [autonomousUnits, setAutonomousUnits] = useState([]);
  const [autonomousUnitStats, setAutonomousUnitStats] = useState(null);
  const [factories, setFactories] = useState([]);

  const refreshState = async () => {
    try {
      // Fetch system data
      const systemResponse = await fetch("/api/system");
      if (systemResponse.ok) {
        const systemData = await systemResponse.json();
        setSystem(systemData);
      }

      // Fetch player units
      const playerResponse = await fetch("/api/player_units/player_1");
      if (playerResponse.ok) {
        const data = await playerResponse.json();
        setPlayerUnits([...data]);
        if (data.length > 0) setUnitDirection(data[0].direction ?? 0);
      }

      // Fetch autonomous units
      const gameStateResponse = await fetch('/api/game_state');
      if (gameStateResponse.ok) {
        const gameState = await gameStateResponse.json();
        const units = Object.values(gameState.autonomous_units || {});
        setAutonomousUnits(units);
      }

      // Fetch autonomous unit statistics
      const statsResponse = await fetch('/api/autonomous_units');
      if (statsResponse.ok) {
        const stats = await statsResponse.json();
        setAutonomousUnitStats(stats);
      }

      // Fetch factories
      const factoriesResponse = await fetch('/api/factories');
      if (factoriesResponse.ok) {
        const factoriesData = await factoriesResponse.json();
        setFactories(factoriesData.factories || []);
      }
    } catch (error) {
      console.error('Failed to refresh state:', error);
    }
  };

  useEffect(() => { 
    refreshState(); 
    
    // Set up periodic refresh for autonomous units
    const interval = setInterval(() => {
      refreshState();
    }, 10000); // Refresh every 10 seconds
    
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === "ArrowLeft") {
        setUnitDirection((prev) => (prev + 1) % 6);
      } else if (event.key === "ArrowRight") {
        setUnitDirection((prev) => (prev + 5) % 6);
      } else if (event.key === "ArrowUp" && playerUnits.length > 0) {
        const unit = playerUnits[0];
        fetch("/api/move_unit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ unit_id: unit.id, direction: unitDirection })
        })
          .then((res) => {
            if (!res.ok) throw new Error("Move failed");
            return res.json();
          })
          .then(() => {
            refreshState();
          })
          .catch((err) => console.error("Move error:", err));
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [playerUnits, unitDirection]);

  return (
    <div className="main-container">
      <div className="map-container">
        {system && (
        <MapView
            system={system}
            playerUnits={playerUnits}
            unitDirection={unitDirection}
            zoom={zoom}
            setZoom={setZoom}
            offset={offset}
            setOffset={setOffset}
            refreshState={refreshState}
            autonomousUnits={autonomousUnits}
            factories={factories}
        />
        )}
      </div>
      <Sidebar 
        system={system} 
        playerUnits={playerUnits} 
        refreshState={refreshState}
        autonomousUnits={autonomousUnits}
        autonomousUnitStats={autonomousUnitStats}
        factories={factories}
      />
    </div>
  );
}

export default GameView;
