import React, { useState, useEffect } from "react";

function ResourceDepositDialog({ structure, playerUnit, onClose, refreshState }) {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [selectedResource, setSelectedResource] = useState("");
  const [depositAmount, setDepositAmount] = useState(1);
  const [availableResources, setAvailableResources] = useState({});

  useEffect(() => {
    if (playerUnit && playerUnit.inventory) {
      // Filter out fuel and only show resources that can be deposited
      const resources = Object.entries(playerUnit.inventory)
        .filter(([resource, amount]) => resource !== 'fuel' && amount > 0)
        .reduce((acc, [resource, amount]) => {
          acc[resource] = amount;
          return acc;
        }, {});
      
      setAvailableResources(resources);
      
      // Auto-select first available resource
      const firstResource = Object.keys(resources)[0];
      if (firstResource && !selectedResource) {
        setSelectedResource(firstResource);
      }
    }
  }, [playerUnit, selectedResource]);

  const handleDeposit = async () => {
    if (!selectedResource || depositAmount <= 0 || !playerUnit) {
      setMessage("Please select a valid resource and amount");
      return;
    }

    const availableAmount = availableResources[selectedResource] || 0;
    if (depositAmount > availableAmount) {
      setMessage(`Not enough ${selectedResource}. Available: ${availableAmount}`);
      return;
    }

    try {
      setLoading(true);
      setMessage("");

      const response = await fetch('http://localhost:5000/api/deposit_resource', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          unit_id: playerUnit.unit_id || playerUnit.id,
          structure_id: structure.id,
          resource_id: selectedResource,
          quantity: depositAmount
        })
      });

      if (response.ok) {
        const result = await response.json();
        setMessage(`✓ Successfully deposited ${depositAmount} ${selectedResource}`);
        
        // Refresh game state
        if (refreshState) {
          setTimeout(() => {
            refreshState();
            onClose();
          }, 1500);
        }
      } else {
        const error = await response.json();
        setMessage(`Failed: ${error.error || 'Unknown error'}`);
      }
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAmountChange = (e) => {
    const value = parseInt(e.target.value) || 0;
    const maxAmount = availableResources[selectedResource] || 0;
    setDepositAmount(Math.min(Math.max(0, value), maxAmount));
  };

  const setMaxAmount = () => {
    const maxAmount = availableResources[selectedResource] || 0;
    setDepositAmount(maxAmount);
  };

  if (!structure || !playerUnit) return null;

  const hasResources = Object.keys(availableResources).length > 0;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center" style={{ zIndex: 10000 }}>
      <div className="bg-gray-900 text-white rounded-lg p-6 max-w-md w-full mx-4 border border-gray-700 shadow-2xl">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Deposit Resources</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-xl"
          >
            ×
          </button>
        </div>

        <div className="mb-4 p-3 bg-gray-800 rounded">
          <div className="text-sm font-medium mb-2">Target: {structure.name}</div>
          <div className="text-xs text-gray-400">Location: {structure.location_space_id}</div>
          {structure.inventory && (
            <div className="mt-2">
              <div className="text-xs font-medium text-gray-300">Current Inventory:</div>
              <div className="grid grid-cols-2 gap-1 mt-1">
                {Object.entries(structure.inventory)
                  .filter(([_, amount]) => amount > 0)
                  .map(([resource, amount]) => (
                    <div key={resource} className="text-xs text-gray-400">
                      {resource}: {amount}
                    </div>
                  ))}
              </div>
            </div>
          )}
        </div>

        {!hasResources ? (
          <div className="text-center py-4">
            <div className="text-gray-400 mb-2">No resources available to deposit</div>
            <div className="text-xs text-gray-500">
              Collect resources first, then return to deposit them.
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Resource to Deposit:</label>
              <select
                value={selectedResource}
                onChange={(e) => setSelectedResource(e.target.value)}
                className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-white"
                disabled={loading}
              >
                <option value="">Select a resource...</option>
                {Object.entries(availableResources).map(([resource, amount]) => (
                  <option key={resource} value={resource}>
                    {resource} (available: {amount})
                  </option>
                ))}
              </select>
            </div>

            {selectedResource && (
              <div>
                <label className="block text-sm font-medium mb-2">
                  Amount (Max: {availableResources[selectedResource]}):
                </label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    min="1"
                    max={availableResources[selectedResource]}
                    value={depositAmount}
                    onChange={handleAmountChange}
                    className="flex-1 p-2 bg-gray-700 border border-gray-600 rounded text-white"
                    disabled={loading}
                  />
                  <button
                    onClick={setMaxAmount}
                    className="px-3 py-2 bg-gray-600 hover:bg-gray-500 rounded text-sm"
                    disabled={loading}
                  >
                    Max
                  </button>
                </div>
              </div>
            )}

            <button
              onClick={handleDeposit}
              disabled={loading || !selectedResource || depositAmount <= 0}
              className={`w-full p-2 rounded font-medium ${
                loading || !selectedResource || depositAmount <= 0
                  ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                  : 'bg-green-600 hover:bg-green-700 text-white'
              }`}
            >
              {loading ? 'Depositing...' : `Deposit ${depositAmount} ${selectedResource || 'Resource'}`}
            </button>
          </div>
        )}

        {message && (
          <div className={`mt-4 p-2 rounded text-sm ${
            message.startsWith('✓') 
              ? 'bg-green-800 text-green-200' 
              : 'bg-red-800 text-red-200'
          }`}>
            {message}
          </div>
        )}
      </div>
    </div>
  );
}

export default ResourceDepositDialog;