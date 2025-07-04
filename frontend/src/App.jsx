import React, { useEffect, useState } from "react";
import "./App.css";

// Constants for layout
const CENTER_X = 600;
const CENTER_Y = 400;
const SUN_RADIUS = 30;
const HEX_RADIUS = 20;
const HEX_WIDTH = Math.sqrt(3) * HEX_RADIUS;
const HEX_HEIGHT = 2 * HEX_RADIUS;
const ORBIT_SPACING = 120;

const polarToCartesian = (angle, radius) => [
  CENTER_X + radius * Math.cos(angle),
  CENTER_Y + radius * Math.sin(angle)
];

const axialToPixel = (q, r) => [
  HEX_WIDTH * (q + r / 2),
  HEX_HEIGHT * (r * 3 / 4)
];

function App() {
  const [system, setSystem] = useState(null);

  useEffect(() => {
    fetch("/api/system")
      .then((res) => res.json())
      .then((data) => {
        console.log("System loaded:", data);
        setSystem(data);
      });
  }, []);

  return (
    <div className="App">
      <h1 style={{ textAlign: "center", color: "#eee" }}>
        {system?.name || "Loading system..."}
      </h1>
      <svg width={1200} height={800} style={{ background: "#0a0a0a" }}>
        {/* Sun at center */}
        <circle cx={CENTER_X} cy={CENTER_Y} r={SUN_RADIUS} fill="orange" />
        <text x={CENTER_X} y={CENTER_Y - 40} textAnchor="middle" fill="white">
          Sun
        </text>

        {/* Bodies and their spaces */}
        {system?.bodies?.map((body, index) => {
          const angle = (index / system.bodies.length) * 2 * Math.PI;
          const orbitRadius = ORBIT_SPACING + index * ORBIT_SPACING;
          const [bodyX, bodyY] = polarToCartesian(angle, orbitRadius);

          return (
            <g key={body.id} transform={`translate(${bodyX}, ${bodyY})`}>
              <text
                x={0}
                y={-HEX_RADIUS * 4}
                textAnchor="middle"
                fill="white"
                fontSize={12}
              >
                {body.name}
              </text>

              {body.spaces?.map((space) => {
                const [x, y] = axialToPixel(space.q, space.r);
                const hexPoints = Array.from({ length: 6 }, (_, i) => {
                  const angle = (Math.PI / 3) * i + Math.PI / 6;
                  const px = x + HEX_RADIUS * Math.cos(angle);
                  const py = y + HEX_RADIUS * Math.sin(angle);
                  return `${px},${py}`;
                }).join(" ");

                return (
                  <polygon
                    key={space.id}
                    points={hexPoints}
                    fill="#ccc"
                    stroke="#333"
                    strokeWidth="1"
                    opacity={0.8}
                  />
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
