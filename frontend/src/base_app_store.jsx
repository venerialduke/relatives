import React, { useEffect, useState } from "react";
import "./App.css";

const CENTER_X = 1000;
const CENTER_Y = 1600;
const HEX_RADIUS = 20;
const HEX_WIDTH = Math.sqrt(3) * HEX_RADIUS;
const HEX_HEIGHT = 2 * HEX_RADIUS;
const DIRECTION_ANGLES = [0, -60, -120, 180, 120, 60]; // degrees, clockwise from East

const axialToPixel = (q, r) => [
  CENTER_X + HEX_WIDTH * (q + r / 2),
  CENTER_Y + HEX_HEIGHT * (r * 3 / 4)
];

const drawHex = (cx, cy) => {
  return Array.from({ length: 6 }, (_, i) => {
    const angle = (Math.PI / 3) * i + Math.PI / 6;
    const x = cx + HEX_RADIUS * Math.cos(angle);
    const y = cy + HEX_RADIUS * Math.sin(angle);
    return `${x},${y}`;
  }).join(" ");
};

function App() {
  const [system, setSystem] = useState(null);
  const [playerUnitSpaces, setPlayerUnitSpaces] = useState([]);
  const [playerUnits, setPlayerUnits] = useState([]);
  const [unitDirection, setUnitDirection] = useState(0);  // <-- NEW
  const [autonomousUnits, setAutonomousUnits] = useState([]);
  const [autonomousUnitStats, setAutonomousUnitStats] = useState(null);
  const [factories, setFactories] = useState([]);

  useEffect(() => {
    fetch("/api/system")
      .then((res) => res.json())
      .then((data) => {
        setSystem(data);
      });

    fetch("/api/player_units/player_1")
      .then((res) => res.json())
      .then((data) => {
        setPlayerUnits(data);
        const spaceIds = data.map((u) => u.space_id);
        setPlayerUnitSpaces(spaceIds);
        if (data.length > 0) {
          setUnitDirection(data[0].direction ?? 0);
        }
      });
  }, []);

  // Fetch autonomous units and factories
  useEffect(() => {
    const fetchAutonomousData = async () => {
      try {
        // Fetch autonomous unit statistics
        const statsResponse = await fetch('/api/autonomous_units');
        if (statsResponse.ok) {
          const stats = await statsResponse.json();
          setAutonomousUnitStats(stats);
        }

        // Fetch actual autonomous units from game state
        const gameStateResponse = await fetch('/api/game_state');
        if (gameStateResponse.ok) {
          const gameState = await gameStateResponse.json();
          const units = Object.values(gameState.autonomous_units || {});
          setAutonomousUnits(units);
        }

        // Fetch factories
        const factoriesResponse = await fetch('/api/factories');
        if (factoriesResponse.ok) {
          const factoriesData = await factoriesResponse.json();
          setFactories(factoriesData.factories || []);
        }
      } catch (error) {
        console.error('Failed to fetch autonomous data:', error);
      }
    };

    fetchAutonomousData();
    
    // Refresh autonomous data every 10 seconds
    const interval = setInterval(fetchAutonomousData, 10000);
    return () => clearInterval(interval);
  }, []);

  // Refresh function for components to trigger updates
  const refreshState = async () => {
    try {
      // Refresh player units
      const playerResponse = await fetch("/api/player_units/player_1");
      if (playerResponse.ok) {
        const data = await playerResponse.json();
        setPlayerUnits(data);
        const spaceIds = data.map((u) => u.space_id);
        setPlayerUnitSpaces(spaceIds);
        if (data.length > 0) {
          setUnitDirection(data[0].direction ?? 0);
        }
      }

      // Refresh autonomous units
      const gameStateResponse = await fetch('/api/game_state');
      if (gameStateResponse.ok) {
        const gameState = await gameStateResponse.json();
        const units = Object.values(gameState.autonomous_units || {});
        setAutonomousUnits(units);
      }

      // Refresh autonomous unit statistics
      const statsResponse = await fetch('/api/autonomous_units');
      if (statsResponse.ok) {
        const stats = await statsResponse.json();
        setAutonomousUnitStats(stats);
      }

      // Refresh factories
      const factoriesResponse = await fetch('/api/factories');
      if (factoriesResponse.ok) {
        const factoriesData = await factoriesResponse.json();
        setFactories(factoriesData.factories || []);
      }
    } catch (error) {
      console.error('Failed to refresh state:', error);
    }
  };

  // ✅ This is now a separate effect, and legal!
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === "ArrowLeft") {
        setUnitDirection((prev) => (prev + 1) % 6); // rotate CCW
      } else if (event.key === "ArrowRight") {
        setUnitDirection((prev) => (prev + 5) % 6); // rotate CW
      } else if (event.key === "ArrowUp" && playerUnits.length > 0) {
        const unit = playerUnits[0]; // ← assuming one unit for now

        fetch("/api/move_unit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            unit_id: unit.unit_id,
            direction: unitDirection
          }),
        })
          .then((res) => {
            if (!res.ok) throw new Error("Move failed");
            return res.json();
          })
          .then((updatedUnit) => {
            // Use the centralized refresh function
            refreshState();
          })
          .catch((err) => console.error("Move error:", err));
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [playerUnits, unitDirection]);




  return (
    <div className="App">
      <h1 style={{ textAlign: "center", color: "#eee" }}>
        {system?.name || "Loading system..."}
      </h1>
      <svg width={4000} height={2000} style={{ background: "#0a0a0a" }}>
        {system?.bodies?.map((body) => {
          const [bx, by] = axialToPixel(body.q, body.r);
          return (
            <g key={body.id}>
              {/* Draw body label */}
              <text
                x={bx}
                y={by - HEX_RADIUS * 1.5}
                textAnchor="middle"
                fill="white"
                fontSize={12}
              >
                {body.name}
              </text>

              {/* Draw body center hex (optional) */}
              <polygon
                points={drawHex(bx, by)}
                fill="orange"
                stroke="#444"
                strokeWidth="1"
              />

              {/* Draw each space */}
              {body.spaces?.map((space) => {
                const [sx, sy] = axialToPixel(space.q, space.r);
                const unitHere = playerUnits.find((u) => u.space_id === space.id);
                const isPlayerUnitHere = !!unitHere;
                const direction = isPlayerUnitHere ? unitDirection : 0;

                return (
                  <g key={space.id}>
                    {/* The hex itself */}
                    <polygon
                      points={drawHex(sx, sy)}
                      fill="#aaa"
                      stroke={isPlayerUnitHere ? "lime" : "#333"}
                      strokeWidth={isPlayerUnitHere ? 3 : 1}
                      opacity={0.9}
                    />

                    {/* Player unit icon */}
                    {isPlayerUnitHere && (
                    <g transform={`translate(${sx}, ${sy}) rotate(${DIRECTION_ANGLES[direction] + 90} 0 0)`}>
                      <polygon
                        points="-6,6 6,6 0,-14"
                        fill="lime"
                        stroke="black"
                        strokeWidth="1"
                      />
                    </g>
                    )}
                  </g>
                );
              })}
            </g>
          );
        })}
      </svg>
    </div>
  );
}

export default App;
