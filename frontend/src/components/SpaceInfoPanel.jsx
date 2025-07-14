import React, { useState, useMemo, useEffect } from "react";

function SpaceInfoPanel({ space, system, playerUnits, onClose, refreshState }) {
  const [currentView, setCurrentView] = useState('space'); // 'space', 'factory', 'deposit'
  const [selectedStructure, setSelectedStructure] = useState(null);

  if (!space) {
    return null;
  }

  // Memoize space information to prevent recalculation on every render
  const spaceInfo = useMemo(() => {
    if (!system?.bodies) {
      return null;
    }
    
    for (const body of system.bodies) {
      const foundSpace = body.spaces?.find(s => s.id === space.id);
      if (foundSpace) {
        return {
          space: foundSpace,
          body: body
        };
      }
    }
    return null;
  }, [space.id, system?.bodies]);

  if (!spaceInfo) {
    return null;
  }

  const { space: spaceDetails, body } = spaceInfo;
  const structures = spaceDetails.buildings || [];
  const resources = spaceDetails.resources || [];
  const playerUnit = playerUnits?.find(unit => unit.space_id === space.id);

  const handleStructureSelect = (structure) => {
    console.log('📋 Structure selected:', structure.name, structure.id);
    setSelectedStructure(structure);
    
    // Determine which view to show based on structure type
    if (structure.name === 'Factory') {
      setCurrentView('factory');
    } else {
      setCurrentView('deposit'); // Default to deposit for other structures
    }
  };

  const handleBackToSpace = () => {
    console.log('🔙 Returning to space view');
    setCurrentView('space');
    setSelectedStructure(null);
  };

  const handleFactoryAction = (action) => {
    console.log('🏭 Factory action:', action);
    if (action === 'deposit') {
      setCurrentView('deposit');
    }
    // Handle other factory actions here
  };

  const closeAll = () => {
    setCurrentView('space');
    setSelectedStructure(null);
    onClose();
  };

  // Only log when panel first opens or space changes
  useEffect(() => {
    console.log('🎨 SpaceInfoPanel opened for space:', space.id);
  }, [space.id]);

  // Debug view changes
  useEffect(() => {
    console.log('🔄 Panel view changed to:', currentView);
  }, [currentView]);

  return (
    <>
      <div 
        className="fixed bottom-0 left-0 right-0 bg-gray-900 border-t-2 border-gray-700 p-4 z-40 max-h-64 overflow-y-auto"
        style={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          backgroundColor: '#111827',
          borderTop: '2px solid #374151',
          padding: '16px',
          zIndex: 40,
          maxHeight: '256px',
          overflowY: 'auto'
        }}
      >
        <div className="flex justify-between items-start mb-3">
          <div className="flex items-center gap-3">
            {currentView !== 'space' && (
              <button
                onClick={handleBackToSpace}
                className="text-blue-400 hover:text-blue-300 text-sm flex items-center gap-1"
              >
                ← Back
              </button>
            )}
            <div>
              <h3 className="text-lg font-bold text-white">
                {currentView === 'space' && `Space: ${spaceDetails.id}`}
                {currentView === 'factory' && `🏭 Factory: ${selectedStructure?.id}`}
                {currentView === 'deposit' && `📦 Deposit to: ${selectedStructure?.name}`}
              </h3>
              <div className="text-sm text-gray-400">
                {currentView === 'space' && `${body.name} • Coordinates: (${spaceDetails.q}, ${spaceDetails.r})`}
                {currentView === 'factory' && 'Manage unit production and factory operations'}
                {currentView === 'deposit' && 'Transfer resources from your unit'}
              </div>
            </div>
          </div>
          <button
            onClick={closeAll}
            className="text-gray-400 hover:text-white text-xl"
          >
            ×
          </button>
        </div>

        {/* View Content */}
        {currentView === 'space' && (
          <SpaceView 
            structures={structures}
            resources={resources}
            playerUnit={playerUnit}
            onStructureSelect={handleStructureSelect}
          />
        )}

        {currentView === 'factory' && selectedStructure && (
          <FactoryView 
            factory={selectedStructure}
            onAction={handleFactoryAction}
            refreshState={refreshState}
          />
        )}

        {currentView === 'deposit' && selectedStructure && (
          <DepositView 
            structure={selectedStructure}
            playerUnit={playerUnit}
            refreshState={refreshState}
          />
        )}

        {/* Action Hints */}
        <div className="mt-3 pt-2 border-t border-gray-700">
          <div className="text-xs text-gray-500 text-center">
            {currentView === 'space' && 'Click structures to interact • Press ESC or click × to close'}
            {currentView !== 'space' && 'Use the Back button to return to space view'}
          </div>
        </div>
      </div>
    </>
  );
}

// Simple Space View Component
function SpaceView({ structures, resources, playerUnit, onStructureSelect }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {/* Player Unit Section */}
      {playerUnit && (
        <div className="bg-gray-800 p-3 rounded">
          <h4 className="font-semibold text-green-400 mb-2">🚀 Your Unit</h4>
          <div className="text-sm space-y-1">
            <div>ID: {playerUnit.unit_id || playerUnit.id}</div>
            <div>Health: {playerUnit.health}</div>
            {playerUnit.inventory && Object.keys(playerUnit.inventory).length > 0 && (
              <div>
                <div className="font-medium text-gray-300">Inventory:</div>
                {Object.entries(playerUnit.inventory)
                  .filter(([_, amount]) => amount > 0)
                  .map(([resource, amount]) => (
                    <div key={resource} className="text-xs text-gray-400 ml-2">
                      {resource}: {amount}
                    </div>
                  ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Structures Section */}
      {structures.length > 0 && (
        <div className="bg-gray-800 p-3 rounded">
          <h4 className="font-semibold text-purple-400 mb-2">🏭 Structures ({structures.length})</h4>
          <div className="space-y-2">
            {structures.map((structure) => (
              <button
                key={structure.id}
                onClick={() => onStructureSelect(structure)}
                className="w-full text-left p-2 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors"
              >
                <div className="font-medium">{structure.name}</div>
                <div className="text-xs text-gray-400">ID: {structure.id}</div>
                {structure.inventory && Object.keys(structure.inventory).length > 0 && (
                  <div className="text-xs text-gray-400 mt-1">
                    Items: {Object.keys(structure.inventory).length}
                  </div>
                )}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Resources Section */}
      {resources.length > 0 && (
        <div className="bg-gray-800 p-3 rounded">
          <h4 className="font-semibold text-yellow-400 mb-2">💎 Resources ({resources.length})</h4>
          <div className="space-y-1">
            {resources.map((resource, index) => (
              <div key={index} className="text-sm">
                <div className="font-medium">{resource.resource_id || resource.name}</div>
                <div className="text-xs text-gray-400">
                  Amount: {resource.amount || resource.quantity || 'Unknown'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty Space Info */}
      {structures.length === 0 && resources.length === 0 && !playerUnit && (
        <div className="bg-gray-800 p-3 rounded col-span-full text-center">
          <div className="text-gray-400">Empty space</div>
          <div className="text-xs text-gray-500 mt-1">
            No structures, resources, or units present
          </div>
        </div>
      )}
    </div>
  );
}

// Simple Factory View Component  
function FactoryView({ factory, onAction, refreshState }) {
  return (
    <div className="space-y-4">
      <div className="bg-gray-800 p-4 rounded">
        <h4 className="font-semibold text-purple-400 mb-3">Factory Operations</h4>
        
        <div className="grid grid-cols-1 gap-3">
          <button
            onClick={() => onAction('build')}
            className="w-full p-3 bg-purple-600 hover:bg-purple-700 rounded font-medium transition-colors"
          >
            🏭 Build Mining Drone
          </button>
          
          <button
            onClick={() => onAction('deposit')}
            className="w-full p-3 bg-green-600 hover:bg-green-700 rounded font-medium transition-colors"
          >
            📦 Deposit Resources
          </button>
        </div>

        <div className="mt-3 p-3 bg-gray-700 rounded">
          <div className="text-sm text-gray-300 mb-2">Factory Status:</div>
          <div className="text-xs space-y-1">
            <div>Ready to build: {factory.can_build_this_turn ? 'Yes' : 'No'}</div>
            <div>Cooldown: {factory.build_cooldown || 0} turns</div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Simple Deposit View Component
function DepositView({ structure, playerUnit, refreshState }) {
  return (
    <div className="space-y-4">
      <div className="bg-gray-800 p-4 rounded">
        <h4 className="font-semibold text-green-400 mb-3">Resource Deposit</h4>
        
        <div className="text-sm text-gray-300 mb-3">
          Coming soon: Deposit resources from your unit to {structure.name}
        </div>

        {playerUnit?.inventory && (
          <div className="p-3 bg-gray-700 rounded">
            <div className="text-sm font-medium text-gray-300 mb-2">Your Inventory:</div>
            {Object.entries(playerUnit.inventory)
              .filter(([resource, amount]) => resource !== 'fuel' && amount > 0)
              .map(([resource, amount]) => (
                <div key={resource} className="text-xs text-gray-400">
                  {resource}: {amount}
                </div>
              ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default SpaceInfoPanel;