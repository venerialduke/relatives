import React from "react";
import { HEX_RADIUS, HEX_DIRECTIONS, polarToCartesian } from "../utils/hexUtils";

const textLabel = (text, x, y, size = "12px", color = "black") =>
  text ? (
    <text x={x} y={y} textAnchor="middle" fontSize={size} fill={color}>
      {text}
    </text>
  ) : null;

const renderHex = (x, y, space, isCurrent, isFacing, isExplored, isSelected, moveUnit, setSelectedSpace, deployingRobot, system, unit, robots, setMessage, setDeployingRobot) => {
  let fill = "#ddd";
  if (isCurrent) fill = "lightgreen";
  else if (isFacing) fill = "purple";
  else if (isSelected) fill = "#66ccff";
  else if (isExplored) fill = "#999";
  else fill = "#eee";

  return (
    <g
      key={space.id}
      transform={`translate(${x},${y})`}
      onContextMenu={(e) => {
        e.preventDefault();
        setSelectedSpace(space);

        if (deployingRobot) {
          const currentSpace = system.bodies
            .flatMap((b) => b.spaces)
            .find((s) => s.id === unit.current_space_id);

          const [dq, dr] = [space.q - currentSpace.q, space.r - currentSpace.r];
          const isAdjacent = HEX_DIRECTIONS.some(([dQ, dR]) => dQ === dq && dR === dr);

          if (!isAdjacent) {
            setMessage("Robots can only be deployed to adjacent spaces.");
            return;
          }

          fetch("/api/deploy_robot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ space_id: space.id }),
          })
            .then((res) => res.json())
            .then((data) => {
              setMessage("Robot deployed.");
              setDeployingRobot(false);
            });
        } else {
          moveUnit(space.id);
        }
      }}
    >
      <polygon
        points={Array.from({ length: 6 }, (_, i) => {
          const angle = Math.PI / 3 * i + Math.PI / 6;
          const px = HEX_RADIUS * Math.cos(angle);
          const py = HEX_RADIUS * Math.sin(angle);
          return `${px},${py}`;
        }).join(" ")}
        fill={fill}
        stroke="#333"
      />
      {textLabel(space.building, 0, 0, "8px", "blue")}
      {robots.some((r) => r.current_space_id === space.id) && (
        <circle cx={0} cy={0} r={5} fill="red" />
      )}
    </g>
  );
};

const MapView = ({
  system,
  unit,
  facingIndex,
  selectedSpace,
  setSelectedSpace,
  moveUnit,
  robots,
  deployingRobot,
  setDeployingRobot,
  setMessage,
}) => {
  const centerX = 600;
  const centerY = 500;

  return (
    <svg width="1200" height="1200">
      <circle cx={centerX} cy={centerY} r={30} fill="orange" />
      {textLabel("Sun", centerX, centerY - 5)}

      {system?.bodies.map((body, bIdx) => {
        const angle = (bIdx / system.bodies.length) * 2 * Math.PI;
        const baseRadius = 300 + body.spaces.length;
        const [bx, by] = polarToCartesian(angle, baseRadius);

        return (
          <g key={body.id} transform={`translate(${centerX + bx},${centerY + by})`}>
            <circle r={5} fill="gray" />
            {textLabel(body.name, 0, -HEX_RADIUS * 4, "14px", "black")}
            {body.spaces.map((space) => {
              const dx = space.q * HEX_RADIUS * Math.sqrt(3);
              const dy = space.r * HEX_RADIUS * 1.5;

              const isCurrent = unit?.current_space_id === space.id;
              const isFacing = (() => {
                if (!unit?.current_space_id) return false;
                const current = body.spaces.find((s) => s.id === unit.current_space_id);
                const [dq, dr] = HEX_DIRECTIONS[facingIndex];
                return space.q === current.q + dq && space.r === current.r + dr;
              })();
              const isExplored = unit?.explored_spaces?.includes(space.id);
              const isSelected = selectedSpace?.id === space.id;

              return renderHex(
                dx,
                dy,
                space,
                isCurrent,
                isFacing,
                isExplored,
                isSelected,
                moveUnit,
                setSelectedSpace,
                deployingRobot,
                system,
                unit,
                robots,
                setMessage,
                setDeployingRobot
              );
            })}
          </g>
        );
      })}
    </svg>
  );
};

export default MapView;