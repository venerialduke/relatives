import React, { useState, useEffect } from "react";
import FactoryDialog from "./FactoryDialog";
import ResourceDepositDialog from "./ResourceDepositDialog";
import Portal from "./Portal";

// Structure type mapping for dialog routing
const STRUCTURE_CAPABILITIES = {
  "Factory": {
    hasUnitBuilding: true,
    hasCollection: true,
    description: "Builds autonomous units and collects resources"
  },
  "Space Port": {
    hasSpaceTravel: true,
    hasCollection: true,
    description: "Enables inter-body travel and collects resources"
  },
  "Collector": {
    hasCollection: true,
    description: "Automatically harvests resources from nearby spaces"
  },
  "Fuel Pump": {
    hasProduction: true,
    description: "Generates 1 fuel per turn"
  },
  "Settlement": {
    hasPopulation: true,
    description: "Houses population and provides research bonuses"
  },
  "Scanner": {
    hasScanning: true,
    description: "Reveals hidden resources and distant spaces"
  }
};

function StructureInteraction({ structure, onClose, refreshState, playerUnits }) {
  const [activeDialog, setActiveDialog] = useState(null);

  // Debug activeDialog changes
  useEffect(() => {
    console.log('🔄 StructureInteraction activeDialog changed to:', activeDialog);
  }, [activeDialog]);

  if (!structure) {
    return null;
  }

  const capabilities = STRUCTURE_CAPABILITIES[structure.name] || {};
  const hasAnyInteraction = Object.values(capabilities).some(cap => 
    typeof cap === 'boolean' && cap
  );

  const handleFactoryInteraction = () => {
    console.log('🏭 Factory button clicked - opening factory dialog via Portal');
    setActiveDialog('factory');
  };

  const handleSpacePortInteraction = () => {
    console.log('🚀 Space Port button clicked');
    // Future: Space Port travel dialog
    console.log("Space Port interaction - travel dialog coming soon");
  };

  const handleCollectionInteraction = () => {
    console.log('📦 Deposit Resources button clicked - opening dialog via Portal');
    setActiveDialog('deposit');
  };

  const closeDialog = () => {
    setActiveDialog(null);
  };

  const closeAll = () => {
    setActiveDialog(null);
    onClose();
  };

  return (
    <>
      <div 
        className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50"
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999
        }}
      >
        <div 
          className="bg-gray-800 text-white rounded-lg p-6 max-w-sm w-full mx-4"
          style={{
            backgroundColor: '#1f2937',
            color: 'white',
            borderRadius: '8px',
            padding: '24px',
            maxWidth: '400px',
            width: '100%',
            margin: '0 16px',
            maxHeight: '80vh',
            overflowY: 'auto'
          }}
        >

          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-bold" style={{ color: 'white' }}>
              🏭 {structure.name}
            </h2>
            <button
              onClick={closeAll}
              className="text-gray-400 hover:text-white text-xl"
            >
              ×
            </button>
          </div>

          {/* Structure Info */}
          <div className="mb-4 p-3 bg-gray-700 rounded">
            <div className="text-sm text-gray-300 mb-2">
              {capabilities.description}
            </div>
            <div className="text-xs text-gray-400">
              Location: {structure.location_space_id}
            </div>
            {structure.inventory && Object.keys(structure.inventory).length > 0 && (
              <div className="mt-2">
                <div className="text-xs font-medium text-gray-300">Inventory:</div>
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

          {/* Interaction Options */}
          {hasAnyInteraction ? (
            <div className="space-y-2">
              {capabilities.hasUnitBuilding && (
                <button
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    handleFactoryInteraction();
                  }}
                  className="w-full p-2 bg-purple-600 hover:bg-purple-700 rounded font-medium transition-colors"
                  style={{
                    width: '100%',
                    padding: '8px',
                    backgroundColor: '#7c3aed',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  🏭 Manage Unit Production
                </button>
              )}

              {capabilities.hasSpaceTravel && (
                <button
                  onClick={handleSpacePortInteraction}
                  className="w-full p-2 bg-blue-600 hover:bg-blue-700 rounded font-medium transition-colors"
                  title="Coming soon: Space Port travel management"
                >
                  🚀 Manage Space Travel
                </button>
              )}

              {capabilities.hasCollection && (
                <button
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    handleCollectionInteraction();
                  }}
                  className="w-full p-2 bg-green-600 hover:bg-green-700 rounded font-medium transition-colors"
                  style={{
                    width: '100%',
                    padding: '8px',
                    backgroundColor: '#059669',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                  title="Deposit resources into this structure"
                >
                  📦 Deposit Resources
                </button>
              )}

              {capabilities.hasProduction && (
                <div className="p-2 bg-orange-700 rounded text-sm">
                  ⚡ Producing: 1 fuel per turn
                </div>
              )}

              {capabilities.hasScanning && (
                <div className="p-2 bg-yellow-700 rounded text-sm">
                  🔍 Revealing nearby resources
                </div>
              )}

              {capabilities.hasPopulation && (
                <div className="p-2 bg-blue-700 rounded text-sm">
                  🏠 Population center active
                </div>
              )}
            </div>
          ) : (
            <div className="text-gray-400 text-sm text-center py-4">
              No interactive capabilities available
            </div>
          )}

          {/* Structure Status Indicators */}
          <div className="mt-4 flex flex-wrap gap-2">
            {structure.structure_type && (
              <span className="px-2 py-1 bg-gray-600 rounded text-xs">
                {structure.structure_type}
              </span>
            )}
            
            {structure.can_build_this_turn !== undefined && (
              <span className={`px-2 py-1 rounded text-xs ${
                structure.can_build_this_turn 
                  ? 'bg-green-600 text-green-100' 
                  : 'bg-red-600 text-red-100'
              }`}>
                {structure.can_build_this_turn ? 'Ready' : 'On Cooldown'}
              </span>
            )}

            {structure.is_operational !== undefined && (
              <span className={`px-2 py-1 rounded text-xs ${
                structure.is_operational 
                  ? 'bg-green-600 text-green-100' 
                  : 'bg-red-600 text-red-100'
              }`}>
                {structure.is_operational ? 'Operational' : 'Offline'}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Dialog Routing - Using Portal to render at document.body level */}
      {activeDialog === 'factory' && (
        <Portal>
          <FactoryDialog
            factory={structure}
            onClose={closeDialog}
            refreshState={refreshState}
          />
        </Portal>
      )}

      {/* Future: Add other dialog types here */}
      {activeDialog === 'spaceport' && (
        // SpacePortDialog component
        null
      )}

      {activeDialog === 'deposit' && (
        <Portal>
          <ResourceDepositDialog
            structure={structure}
            playerUnit={playerUnits?.[0]}
            onClose={closeDialog}
            refreshState={refreshState}
          />
        </Portal>
      )}
    </>
  );
}

export default StructureInteraction;