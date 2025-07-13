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

  const refreshState = () => {
    fetch("/api/system")
      .then((res) => res.json())
      .then(setSystem);

    fetch("/api/player_units/player_1")
      .then((res) => res.json())
      .then((data) => {
        setPlayerUnits([...data]);
        if (data.length > 0) setUnitDirection(data[0].direction ?? 0);
      });
  };

  useEffect(() => { refreshState(); }, []);

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
            return fetch("/api/player_units/player_1")
              .then((res) => res.json())
              .then((units) => {
                setPlayerUnits(units);
                if (units.length > 0) setUnitDirection(units[0].direction ?? 0);
              });
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
        />
        )}
      </div>
      <Sidebar system={system} playerUnits={playerUnits} refreshState={refreshState} />
    </div>
  );
}

export default GameView;
