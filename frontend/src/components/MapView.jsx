import React, { useState, useEffect, useRef } from "react";
import { axialToPixel, drawHex, DIRECTION_ANGLES } from "./helpers";

function MapView({ system, playerUnits, unitDirection, zoom, setZoom, offset, setOffset }) {

  if (!offset || zoom === undefined) {
    return null; // or a loading placeholder if you prefer
  }
  const svgRef = useRef(null);

  // --- Handle zoom via mouse scroll ---

  // --- Handle pan via WASD ---
  useEffect(() => {
    const handleKeyDown = (e) => {
      const speed = 20;
      switch (e.key.toLowerCase()) {
        case "w":
          setOffset((prev) => ({ ...prev, y: prev.y + speed }));
          break;
        case "s":
          setOffset((prev) => ({ ...prev, y: prev.y - speed }));
          break;
        case "a":
          setOffset((prev) => ({ ...prev, x: prev.x + speed }));
          break;
        case "d":
          setOffset((prev) => ({ ...prev, x: prev.x - speed }));
          break;
        default:
          break;
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return;

    const handleWheel = (e) => {
      e.preventDefault();
      const delta = e.deltaY > 0 ? -0.1 : 0.1;
      setZoom((z) => Math.min(3, Math.max(0.5, z + delta)));
    };

    svg.addEventListener("wheel", handleWheel, { passive: false });

    return () => svg.removeEventListener("wheel", handleWheel);
  }, []);

  return (
    <svg
      ref={svgRef}
      width="100%"
      height="100%"
      style={{ background: "#0a0a0a", display: "block" }}
    >
      <g transform={`translate(${offset.x}, ${offset.y}) scale(${zoom})`}>
        {system?.bodies?.map((body) => {
          const [bx, by] = axialToPixel(body.q, body.r);
          return (
            <g key={body.id}>
              <text
                x={bx}
                y={by - 30}
                textAnchor="middle"
                fill="white"
                fontSize={12}
              >
                {body.name}
              </text>

              <polygon
                points={drawHex(bx, by)}
                fill="orange"
                stroke="#444"
                strokeWidth="1"
              />

              {body.spaces?.map((space) => {
                const [sx, sy] = axialToPixel(space.q, space.r);
                const unitHere = playerUnits.find((u) => u.location_space_id === space.id);
                const isPlayerUnitHere = !!unitHere;
                const direction = isPlayerUnitHere ? unitDirection : 0;

                return (
                  <g key={space.id}>
                    <polygon
                      points={drawHex(sx, sy)}
                      fill="#aaa"
                      stroke={isPlayerUnitHere ? "lime" : "#333"}
                      strokeWidth={isPlayerUnitHere ? 3 : 1}
                      opacity={0.9}
                    />

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
      </g>
    </svg>
  );
}

export default MapView;