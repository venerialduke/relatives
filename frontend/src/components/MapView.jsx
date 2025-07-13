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

// Generate star field data
const generateStarField = (count, width, height) => {
  const stars = [];
  for (let i = 0; i < count; i++) {
    stars.push({
      id: i,
      x: Math.random() * width,
      y: Math.random() * height,
      size: Math.random() * 2 + 0.5,
      brightness: Math.random() * 0.8 + 0.2,
      twinkleSpeed: Math.random() * 3 + 1,
      twinkleOffset: Math.random() * Math.PI * 2
    });
  }
  return stars;
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
  const [starFields] = useState(() => ({
    distant: generateStarField(100, 4000, 4000),
    medium: generateStarField(200, 3000, 3000), 
    close: generateStarField(150, 2000, 2000)
  }));
  const [time, setTime] = useState(0);
  const [backgroundImage] = useState(() => {
    // Randomly select a Hubble image (1-5) when component mounts
    const imageNumber = Math.floor(Math.random() * 5) + 1;
    return `/images/hubble/hubble_${imageNumber}.png`;
  });

  // Get player's explored spaces and system-wide accessible spaces
  const playerUnit = playerUnits?.[0];
  const unitExploredSpaces = new Set(playerUnit?.explored_spaces || []);
  
  // System-wide accessible spaces (first space of each body)
  const systemAccessibleSpaces = new Set();
  system?.bodies?.forEach(body => {
    if (body.spaces && body.spaces.length > 0) {
      systemAccessibleSpaces.add(body.spaces[0].id); // First space is always accessible
    }
  });
  
  // Combined for resource highlighting (existing functionality)
  const exploredSpaces = new Set([...unitExploredSpaces, ...systemAccessibleSpaces]);

  // Animation loop for twinkling stars
  useEffect(() => {
    const animate = () => {
      setTime(prev => prev + 0.016); // ~60fps
      requestAnimationFrame(animate);
    };
    const animationId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationId);
  }, []);

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

  // Calculate ring number that would contain all spaces, then add 1 for outline
  // Formula: total hexes in rings 0 to N = 1 + 3*N*(N+1)
  const calculateRingNumber = (spaceCount) => {
    if (spaceCount <= 1) return 1; // Single hex needs ring 1 outline
    
    // Find the ring that contains this number of spaces
    for (let ring = 1; ring <= 10; ring++) {
      const totalHexes = 1 + 3 * ring * (ring + 1);
      if (spaceCount <= totalHexes) {
        return ring + 1; // Return ring + 1 for the outline
      }
    }
    return Math.ceil(Math.sqrt(spaceCount / 3)) + 1; // Fallback for very large bodies
  };

  // Generate hex ring outline coordinates
  const generateRingOutline = (centerQ, centerR, ring) => {
    // Validate inputs
    if (isNaN(centerQ) || isNaN(centerR) || isNaN(ring)) {
      console.warn('Invalid coordinates for ring outline:', centerQ, centerR, ring);
      return [];
    }
    
    const [centerX, centerY] = axialToPixel(centerQ, centerR);
    
    // Validate pixel coordinates
    if (isNaN(centerX) || isNaN(centerY)) {
      console.warn('Invalid pixel coordinates:', centerX, centerY);
      return [];
    }
    
    if (ring === 0) {
      // Single hex outline - use drawHex and parse properly
      const hexString = drawHex(centerX, centerY);
      const points = hexString.split(' ').map(coord => {
        const [x, y] = coord.split(',').map(Number);
        return [x, y];
      });
      return points;
    }
    
    // For rings > 0, create a larger hexagon outline
    const hexSize = 20; // Match HEX_RADIUS from helpers
    const scaleFactor = ring + 3; // Add extra padding beyond the calculated outline ring
    
    // Generate hexagon vertices at scaled size with flat edges at top/bottom
    const points = [];
    for (let i = 0; i < 6; i++) {
      const angle = (Math.PI / 3) * i; // Remove the +Math.PI/6 offset for flat edges at top/bottom
      const x = centerX + (hexSize * scaleFactor) * Math.cos(angle);
      const y = centerY + (hexSize * scaleFactor) * Math.sin(angle);
      points.push([x, y]);
    }
    
    return points;
  };

  // Generate outline path for body using ring method
  const generateBodyOutline = (body) => {
    if (!body.spaces || body.spaces.length === 0) return '';
    
    const spaceCount = body.spaces.length;
    const ring = calculateRingNumber(spaceCount);
    
    // Debug ring calculation for Planet 4
    if (body.name === 'Planet 4') {
      console.log(`Planet 4 debug: ${spaceCount} spaces, calculated ring: ${ring}`);
      // Test what the actual ring should be
      for (let testRing = 0; testRing <= 5; testRing++) {
        const totalHexes = 1 + 3 * testRing * (testRing + 1);
        console.log(`Ring ${testRing}: total hexes = ${totalHexes}`);
      }
    }
    
    // Use the body's center position directly (body.q, body.r)
    // The ring outline should be centered on the body, not relative coordinates
    const centerQ = body.q;
    const centerR = body.r;
    
    // Validate body coordinates
    if (isNaN(centerQ) || isNaN(centerR)) {
      console.warn('Invalid body coordinates for', body.name, ':', centerQ, centerR);
      return '';
    }
    
    // Generate ring outline
    const ringPoints = generateRingOutline(centerQ, centerR, ring);
    if (ringPoints.length === 0) return '';
    
    // Validate all points before creating path
    const validPoints = ringPoints.filter(point => 
      !isNaN(point[0]) && !isNaN(point[1])
    );
    
    if (validPoints.length === 0) return '';
    
    // Create SVG path
    let path = `M ${validPoints[0][0]} ${validPoints[0][1]} `;
    for (let i = 1; i < validPoints.length; i++) {
      path += `L ${validPoints[i][0]} ${validPoints[i][1]} `;
    }
    path += 'Z';
    
    return path;
  };

  // Render star field with parallax effect
  const renderStarField = (stars, parallaxFactor, className) => {
    // Performance optimization: render fewer stars when zoomed out
    const starCount = Math.min(stars.length, Math.max(50, stars.length * zoom));
    const visibleStars = stars.slice(0, Math.floor(starCount));
    
    return visibleStars.map(star => {
      const parallaxX = offset.x * parallaxFactor;
      const parallaxY = offset.y * parallaxFactor;
      const x = (star.x + parallaxX) % 4000; // Wrap around
      const y = (star.y + parallaxY) % 4000;
      
      // Twinkling effect
      const twinkle = Math.sin(time * star.twinkleSpeed + star.twinkleOffset) * 0.3 + 0.7;
      const opacity = star.brightness * twinkle;
      
      return (
        <circle
          key={`${className}-${star.id}`}
          cx={x}
          cy={y}
          r={star.size * zoom} // Scale star size with zoom
          fill="white"
          opacity={opacity}
          className={className}
        />
      );
    });
  };


  return (
    <div style={{ position: "relative", width: "100%", height: "100%" }}>
      <svg
        ref={svgRef}
        width="100%"
        height="100%"
        style={{ 
          background: `linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url('${backgroundImage}')`, 
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
          display: "block",
          cursor: isDragging ? "grabbing" : "grab"
        }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onContextMenu={handleContextMenu}
      >
        {/* Background star fields with parallax */}
        <g className="star-field-distant">
          {renderStarField(starFields.distant, 0.1, "star-distant")}
        </g>
        <g className="star-field-medium">
          {renderStarField(starFields.medium, 0.3, "star-medium")}
        </g>
        <g className="star-field-close">
          {renderStarField(starFields.close, 0.6, "star-close")}
        </g>

        {/* Game content with normal transform */}
        <g transform={`translate(${offset.x}, ${offset.y}) scale(${zoom})`}>
        {system?.bodies?.map((body) => {
          const [bx, by] = axialToPixel(body.q, body.r);
          const outlinePath = generateBodyOutline(body);
          
          return (
            <g key={body.id}>
              {/* Body outline - bright and prominent */}
              {outlinePath && (
                <path
                  d={outlinePath}
                  fill="none"
                  stroke="#00FFFF"
                  strokeWidth="3"
                  opacity="0.8"
                  style={{
                    filter: 'drop-shadow(0 0 8px #00FFFF)'
                  }}
                />
              )}
              
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
                
                // Determine exploration status for fog-of-war
                const isUnitExplored = unitExploredSpaces.has(space.id);
                const isSystemAccessible = systemAccessibleSpaces.has(space.id);
                const isFullyExplored = exploredSpaces.has(space.id); // For resource highlighting
                
                // Determine fill color and opacity based on exploration status
                let fillColor;
                let opacity = 0.9;
                
                if (isUnitExplored) {
                  fillColor = "#aaa"; // Fully explored (light gray)
                  opacity = 0.9;
                } else if (isSystemAccessible) {
                  fillColor = "#666"; // System accessible (medium gray)
                  opacity = 0.8;
                } else {
                  fillColor = "#333"; // Unexplored (dark gray)
                  opacity = 0.6;
                }
                
                // Check if this space should be highlighted for resources
                const hasSelectedResource = selectedResource && isFullyExplored && 
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
                      fill={fillColor}
                      stroke={strokeColor}
                      strokeWidth={strokeWidth}
                      opacity={opacity}
                    />

                    {/* Show structures on this space (only if explored) */}
                    {isFullyExplored && space.buildings?.map((structure, index) => {
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