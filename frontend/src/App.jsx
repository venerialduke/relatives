import React, { useEffect, useState } from "react";
import "./App.css";

const CENTER_X = 1000;
const CENTER_Y = 1600;
const HEX_RADIUS = 20;
const HEX_WIDTH = Math.sqrt(3) * HEX_RADIUS;
const HEX_HEIGHT = 2 * HEX_RADIUS;

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
                return (
                  <polygon
                    key={space.id}
                    points={drawHex(sx, sy)}
                    fill="#aaa"
                    stroke="#333"
                    strokeWidth="1"
                    opacity={0.9}
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
