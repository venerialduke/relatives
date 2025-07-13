import React, { useState } from "react";

function ResourceCollector({ currentSpace, playerUnit, refreshState }) {
  const [selectedResource, setSelectedResource] = useState("");
  const [selectedSource, setSelectedSource] = useState("space");
  const [selectedStructure, setSelectedStructure] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [isCollecting, setIsCollecting] = useState(false);
  const [message, setMessage] = useState("");

  if (!currentSpace) {
    return null;
  }

  // Get space resources
  const spaceResources = currentSpace.named_inventory ? 
    Object.entries(currentSpace.named_inventory).filter(([, amount]) => amount > 0) : [];

  // Get structure resources
  const structuresWithResources = currentSpace.buildings ? 
    currentSpace.buildings.filter(structure => 
      structure.named_inventory && 
      Object.keys(structure.named_inventory).length > 0
    ) : [];

  // No resources available anywhere
  if (spaceResources.length === 0 && structuresWithResources.length === 0) {
    return (
      <div className="resource-collector">
        <h4>Collect Resources</h4>
        <p>No resources available to collect.</p>
      </div>
    );
  }

  // Get available resources based on selected source
  const getAvailableResources = () => {
    if (selectedSource === "space") {
      return spaceResources;
    } else if (selectedSource === "structure" && selectedStructure) {
      const structure = structuresWithResources.find(s => s.id === selectedStructure);
      return structure ? Object.entries(structure.named_inventory).filter(([, amount]) => amount > 0) : [];
    }
    return [];
  };

  const getMaxQuantity = () => {
    if (!selectedResource) return 0;
    
    if (selectedSource === "space") {
      return currentSpace.named_inventory?.[selectedResource] || 0;
    } else if (selectedSource === "structure" && selectedStructure) {
      const structure = structuresWithResources.find(s => s.id === selectedStructure);
      return structure?.named_inventory?.[selectedResource] || 0;
    }
    return 0;
  };

  const maxQuantity = getMaxQuantity();
  const availableResources = getAvailableResources();

  const handleCollect = async () => {
    if (!selectedResource || quantity <= 0) {
      setMessage("Please select a resource and valid quantity.");
      return;
    }

    if (selectedSource === "structure" && !selectedStructure) {
      setMessage("Please select a structure.");
      return;
    }

    setIsCollecting(true);
    setMessage("");

    try {
      const requestBody = {
        unit_id: playerUnit.id,
        resource_id: selectedResource,
        quantity: quantity
      };

      if (selectedSource === "structure") {
        requestBody.structure_id = selectedStructure;
      }

      const response = await fetch("/api/collect_item", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody)
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(`✓ ${data.result}`);
        setSelectedResource("");
        setQuantity(1);
        if (refreshState) {
          refreshState();
        }
      } else {
        setMessage(`Error: ${data.error || "Collection failed"}`);
      }
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setIsCollecting(false);
    }
  };

  return (
    <div className="resource-collector">
      <h4>Collect Resources</h4>
      
      <div className="collection-controls">
        <label>
          Source:
          <select 
            value={selectedSource} 
            onChange={(e) => {
              setSelectedSource(e.target.value);
              setSelectedResource("");
              setSelectedStructure("");
              setQuantity(1);
            }}
            disabled={isCollecting}
          >
            {spaceResources.length > 0 && <option value="space">Space</option>}
            {structuresWithResources.length > 0 && <option value="structure">Structures</option>}
          </select>
        </label>

        {selectedSource === "structure" && (
          <label>
            Structure:
            <select 
              value={selectedStructure} 
              onChange={(e) => {
                setSelectedStructure(e.target.value);
                setSelectedResource("");
                setQuantity(1);
              }}
              disabled={isCollecting}
            >
              <option value="">Select structure...</option>
              {structuresWithResources.map((structure) => (
                <option key={structure.id} value={structure.id}>
                  {structure.name}
                </option>
              ))}
            </select>
          </label>
        )}

        <label>
          Resource:
          <select 
            value={selectedResource} 
            onChange={(e) => {
              setSelectedResource(e.target.value);
              setQuantity(1);
            }}
            disabled={isCollecting || (selectedSource === "structure" && !selectedStructure)}
          >
            <option value="">Select resource...</option>
            {availableResources.map(([resourceName, amount]) => (
              <option key={resourceName} value={resourceName}>
                {resourceName} ({amount} available)
              </option>
            ))}
          </select>
        </label>

        <label>
          Quantity:
          <input
            type="number"
            min="1"
            max={maxQuantity}
            value={quantity}
            onChange={(e) => setQuantity(Math.min(maxQuantity, Math.max(1, parseInt(e.target.value) || 1)))}
            disabled={!selectedResource || isCollecting}
          />
        </label>

        <button 
          onClick={handleCollect}
          disabled={!selectedResource || quantity <= 0 || isCollecting || (selectedSource === "structure" && !selectedStructure)}
        >
          {isCollecting ? "Collecting..." : "Collect"}
        </button>
      </div>

      {message && (
        <div className={`collection-message ${message.startsWith('✓') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}
    </div>
  );
}

export default ResourceCollector;