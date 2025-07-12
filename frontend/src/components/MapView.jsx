import React, { useState, useEffect, useRef } from "react";
import { axialToPixel, drawHex, DIRECTION_ANGLES } from "./helpers";
import ResourceHighlighter from "./ResourceHighlighter";

// Helper functions for structure visualization
const getStructureColor = (structureName) => {
  const colors = {
    "Fuel Pump": "#FF9800",    // Orange
    "Collector": "#4CAF50",    // Green  
    "Factory": "#9C27B0",      // Purple
    "Settlement": "#2196F3",   // Blue
    "Scanner": "#FFEB3B"       // Yellow
  };
  return colors[structureName] || "#666";
};

const getStructureSymbol = (structureName) => {
  const symbols = {
    "Fuel Pump": "F",
    "Collector": "C", 
    "Factory": "M",
    "Settlement": "S",
    "Scanner": "R"
  };
  return symbols[structureName] || "?";
};

function MapView({ system, playerUnits, unitDirection, zoom, setZoom, offset, setOffset }) {

  if (!offset || zoom === undefined) {
    return null; // or a loading placeholder if you prefer
  }
  const svgRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [selectedResource, setSelectedResource] = useState(null);
  const [highlighterVisible, setHighlighterVisible] = useState(false);

  // Get player's explored spaces
  const playerUnit = playerUnits?.[0];
  const exploredSpaces = new Set(playerUnit?.explored_spaces || []);

  // --- Handle zoom via mouse scroll ---


  useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return;

    const handleWheel = (e) => {
      e.preventDefault();
      
      // Get mouse position relative to SVG
      const rect = svg.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;
      
      const delta = e.deltaY > 0 ? -0.1 : 0.1;
      const newZoom = Math.min(3, Math.max(0.5, zoom + delta));
      
      if (newZoom !== zoom) {
        // Calculate world coordinates under mouse
        const worldX = (mouseX - offset.x) / zoom;
        const worldY = (mouseY - offset.y) / zoom;
        
        // Adjust offset to keep that point under mouse
        const newOffset = {
          x: mouseX - worldX * newZoom,
          y: mouseY - worldY * newZoom
        };
        
        setZoom(newZoom);
        setOffset(newOffset);
      }
    };

    svg.addEventListener("wheel", handleWheel, { passive: false });

    return () => svg.removeEventListener("wheel", handleWheel);
  }, [zoom, offset, setZoom, setOffset]);

  // --- Handle right-click drag ---
  const handleMouseDown = (e) => {
    if (e.button === 2) { // Right click
      e.preventDefault();
      setIsDragging(true);
      setDragStart({ x: e.clientX, y: e.clientY });
    }
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      e.preventDefault();
      const deltaX = e.clientX - dragStart.x;
      const deltaY = e.clientY - dragStart.y;
      
      setOffset(prev => ({
        x: prev.x + deltaX,
        y: prev.y + deltaY
      }));
      
      setDragStart({ x: e.clientX, y: e.clientY });
    }
  };

  const handleMouseUp = (e) => {
    if (e.button === 2) { // Right click
      setIsDragging(false);
    }
  };

  const handleContextMenu = (e) => {
    e.preventDefault(); // Prevent right-click context menu
  };

  return (
    <div style={{ position: "relative", width: "100%", height: "100%" }}>
      <svg
        ref={svgRef}
        width="100%"
        height="100%"
        style={{ 
          background: "#0a0a0a", 
          display: "block",
          cursor: isDragging ? "grabbing" : "grab"
        }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onContextMenu={handleContextMenu}
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
                
                // Check if this space should be highlighted
                const isExplored = exploredSpaces.has(space.id);
                const hasSelectedResource = selectedResource && isExplored && 
                  space.named_inventory && space.named_inventory[selectedResource] > 0;
                
                // Determine stroke properties
                let strokeColor = "#333";
                let strokeWidth = 1;
                
                if (isPlayerUnitHere) {
                  strokeColor = "lime";
                  strokeWidth = 3;
                } else if (hasSelectedResource) {
                  strokeColor = "#FFD700"; // Gold highlight
                  strokeWidth = 3;
                }

                return (
                  <g key={space.id}>
                    <polygon
                      points={drawHex(sx, sy)}
                      fill="#aaa"
                      stroke={strokeColor}
                      strokeWidth={strokeWidth}
                      opacity={0.9}
                    />

                    {/* Show structures on this space */}
                    {space.buildings?.map((structure, index) => {
                      // Position structures in center, spread vertically if multiple
                      const offsetY = space.buildings.length > 1 ? (index - (space.buildings.length - 1) / 2) * 10 : 0;
                      return (
                        <g key={structure.id} transform={`translate(${sx}, ${sy + offsetY})`}>
                          <rect
                            x="-6"
                            y="-6"
                            width="12"
                            height="12"
                            fill={getStructureColor(structure.name)}
                            stroke="#000"
                            strokeWidth="1"
                            opacity="0.9"
                          />
                          <text
                            x="0"
                            y="3"
                            textAnchor="middle"
                            fill="white"
                            fontSize="8"
                            fontWeight="bold"
                          >
                            {getStructureSymbol(structure.name)}
                          </text>
                        </g>
                      );
                    })}

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

    <ResourceHighlighter
      selectedResource={selectedResource}
      onResourceSelect={setSelectedResource}
      isVisible={highlighterVisible}
      onToggleVisibility={() => setHighlighterVisible(!highlighterVisible)}
    />
  </div>
  );
}

export default MapView;