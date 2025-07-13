import React, { useState } from "react";

const RESOURCE_TABLE = [
  ["Iron", "Crystal", "Gas", "Ice", "Silver", "Algae"],
  ["Silicon", "Copper", "Sand", "Carbon", "Nickel", "Stone"],
  ["Obsidian", "Quartz", "Dust", "Water", "Oil", "Fish"],
  ["Plasma", "Fungus", "Xenonite", "Ore", "SpaceDust", "Fuel"]
];

const RESOURCE_SYMBOLS = {
  "Iron": "Fe", "Crystal": "Cr", "Gas": "Ga", "Ice": "Ic", "Silver": "Ag", "Algae": "Al",
  "Silicon": "Si", "Copper": "Cu", "Sand": "Sa", "Carbon": "Ca", "Nickel": "Ni", "Stone": "St",
  "Obsidian": "Ob", "Quartz": "Qz", "Dust": "Du", "Water": "Wa", "Oil": "Oi", "Fish": "Fi",
  "Plasma": "Pl", "Fungus": "Fu", "Xenonite": "Xe", "Ore": "Or", "SpaceDust": "SD", "Fuel": "Fl"
};

const RESOURCE_COLORS = {
  "Iron": "#BDC3C7", "Crystal": "#9B59B6", "Gas": "#3498DB", "Ice": "#AED6F1", "Silver": "#D5DBDB", "Algae": "#58D68D",
  "Silicon": "#85929E", "Copper": "#D35400", "Sand": "#F4D03F", "Carbon": "#2C3E50", "Nickel": "#A6ACAF", "Stone": "#797D7F",
  "Obsidian": "#1B2631", "Quartz": "#F8C471", "Dust": "#CCD1D1", "Water": "#5DADE2", "Oil": "#2E4057", "Fish": "#FF6B6B",
  "Plasma": "#E74C3C", "Fungus": "#27AE60", "Xenonite": "#8E44AD", "Ore": "#E67E22", "SpaceDust": "#95A5A6", "Fuel": "#F39C12"
};

function ResourceHighlighter({ selectedResource, onResourceSelect, isVisible, onToggleVisibility }) {
  
  const handleResourceClick = (resource) => {
    if (selectedResource === resource) {
      onResourceSelect(null); // Deselect if clicking same resource
    } else {
      onResourceSelect(resource);
    }
  };

  return (
    <div className="resource-highlighter">
      <button 
        className="resource-highlighter-toggle"
        onClick={onToggleVisibility}
        title="Toggle Resource Highlighter"
      >
        🔍
      </button>
      
      {isVisible && (
        <div className="resource-table-container">
          <div className="resource-table-header">
            <span>Resource Highlighter</span>
            <button 
              className="clear-button"
              onClick={() => onResourceSelect(null)}
              disabled={!selectedResource}
            >
              Clear
            </button>
          </div>
          
          <div className="resource-table">
            {RESOURCE_TABLE.map((row, rowIndex) => (
              <div key={rowIndex} className="resource-row">
                {row.map((resource) => (
                  <button
                    key={resource}
                    className={`resource-element ${selectedResource === resource ? 'selected' : ''}`}
                    style={{
                      backgroundColor: RESOURCE_COLORS[resource],
                      color: resource === "Obsidian" || resource === "Carbon" || resource === "Oil" ? "#FFF" : "#000"
                    }}
                    onClick={() => handleResourceClick(resource)}
                    title={resource}
                  >
                    {RESOURCE_SYMBOLS[resource]}
                  </button>
                ))}
              </div>
            ))}
          </div>
          
          {selectedResource && (
            <div className="selected-resource-info">
              Highlighting: <strong>{selectedResource}</strong>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default ResourceHighlighter;