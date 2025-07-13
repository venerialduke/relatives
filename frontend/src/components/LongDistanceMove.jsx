import React, { useState, useEffect } from 'react';

function LongDistanceMove({ playerUnit, isVisible, onClose, onMoveComplete }) {
  const [movementOptions, setMovementOptions] = useState(null);
  const [selectedBody, setSelectedBody] = useState(null);
  const [selectedSpace, setSelectedSpace] = useState(null);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isVisible && playerUnit) {
      fetchMovementOptions();
    }
  }, [isVisible, playerUnit]);

  const fetchMovementOptions = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/movement_options?unit_id=${playerUnit.id}`);
      if (!response.ok) throw new Error('Failed to fetch movement options');
      const data = await response.json();
      setMovementOptions(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDestinationSelect = (destination) => {
    setSelectedSpace(destination);
    setShowConfirmation(true);
  };

  // Build unified destination list with minimum costs
  const getAllDestinations = () => {
    if (!movementOptions) return [];
    
    const destinations = [];
    
    // Add Space Port destinations (higher priority, lower cost)
    if (movementOptions.space_port_destinations) {
      movementOptions.space_port_destinations.forEach(dest => {
        destinations.push({
          space_id: dest.space_id,
          name: `${dest.space_name} (${dest.body_name})`,
          display_name: dest.space_name,
          body_name: dest.body_name,
          cost: dest.fuel_cost,
          travel_type: 'Space Port',
          icon: '🚀'
        });
      });
    }
    
    // Add regular inter-body destinations (only if no Space Port route exists)
    if (movementOptions.reachable_bodies) {
      movementOptions.reachable_bodies.forEach(body => {
        body.explored_spaces.forEach(space => {
          // Check if this destination already has a Space Port route
          const hasSpacePortRoute = destinations.some(dest => dest.space_id === space.space_id);
          if (!hasSpacePortRoute) {
            destinations.push({
              space_id: space.space_id,
              name: `${space.name} (${body.name})`,
              display_name: space.name,
              body_name: body.name,
              cost: movementOptions.inter_body_cost,
              travel_type: 'Inter-body',
              icon: '🌍'
            });
          }
        });
      });
    }
    
    return destinations.sort((a, b) => a.cost - b.cost || a.name.localeCompare(b.name));
  };

  const confirmMove = async () => {
    if (!selectedSpace) return;

    try {
      setLoading(true);
      const response = await fetch('/api/move_unit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          unit_id: playerUnit.id,
          direction: null, // Not used for direct space movement
          space_id: selectedSpace.space_id
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Move failed');
      }

      onMoveComplete();
      handleClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setSelectedBody(null);
    setSelectedSpace(null);
    setShowConfirmation(false);
    setError(null);
    onClose();
  };

  if (!isVisible) return null;

  const destinations = getAllDestinations();
  const currentFuel = movementOptions?.current_fuel || 0;

  return (
    <div className="modal-overlay">
      <div className="modal-content long-distance-modal">
        <div className="modal-header">
          <h3>Long Distance Movement</h3>
          <button onClick={handleClose} className="close-button">×</button>
        </div>

        {loading && <div className="loading">Loading...</div>}
        {error && <div className="error-message">{error}</div>}

        {movementOptions && (
          <div className="modal-body">
            <div className="fuel-status">
              <span className="fuel-amount">
                Available Fuel: {currentFuel}
              </span>
            </div>

            {destinations.length === 0 ? (
              <div className="no-destinations">
                No destinations available. Explore more spaces to unlock travel options.
              </div>
            ) : (
              <div className="destinations-section">
                <h4>Available Destinations</h4>
                <div className="destinations-grid">
                  {destinations.map((destination) => {
                    const canAfford = currentFuel >= destination.cost;
                    return (
                      <div 
                        key={destination.space_id}
                        className={`destination-card destination-pill ${canAfford ? 'affordable' : 'unaffordable'}`}
                        onClick={() => canAfford && handleDestinationSelect(destination)}
                        style={{ 
                          cursor: canAfford ? 'pointer' : 'not-allowed',
                          border: '2px solid #ddd',
                          borderRadius: '12px',
                          padding: '12px',
                          margin: '8px 0',
                          backgroundColor: canAfford ? '#f8f9fa' : '#f5f5f5',
                          transition: 'all 0.2s ease',
                          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                        }}
                        onMouseEnter={(e) => {
                          if (canAfford) {
                            e.target.style.backgroundColor = '#e9ecef';
                            e.target.style.borderColor = '#007bff';
                            e.target.style.transform = 'translateY(-2px)';
                            e.target.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
                          }
                        }}
                        onMouseLeave={(e) => {
                          if (canAfford) {
                            e.target.style.backgroundColor = '#f8f9fa';
                            e.target.style.borderColor = '#ddd';
                            e.target.style.transform = 'translateY(0)';
                            e.target.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
                          }
                        }}
                      >
                        <div className="destination-header">
                          <span className="travel-icon">{destination.icon}</span>
                          <div className="destination-info">
                            <h5>{destination.display_name}</h5>
                            <span className="body-name">{destination.body_name}</span>
                          </div>
                        </div>
                        <div className="destination-footer">
                          <span className="travel-type">{destination.travel_type}</span>
                          <span className={`fuel-cost ${canAfford ? 'affordable-cost' : 'unaffordable-cost'}`}>
                            {destination.cost} fuel
                          </span>
                        </div>
                        {!canAfford && (
                          <div className="insufficient-fuel-overlay">
                            Need {destination.cost - currentFuel} more fuel
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}

        {showConfirmation && selectedSpace && (
          <div className="confirmation-overlay">
            <div className="confirmation-dialog">
              <h4>Confirm Movement</h4>
              <p>Move to <strong>{selectedSpace.name}</strong>?</p>
              <p>Travel type: <strong>{selectedSpace.travel_type}</strong> {selectedSpace.icon}</p>
              <p>This will cost <strong>{selectedSpace.cost} fuel</strong></p>
              <p>Remaining fuel: <strong>{currentFuel - selectedSpace.cost}</strong></p>
              <div className="confirmation-buttons">
                <button onClick={() => setShowConfirmation(false)} className="cancel-button">
                  Cancel
                </button>
                <button onClick={confirmMove} className="confirm-button" disabled={loading}>
                  {loading ? 'Moving...' : 'Confirm Move'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default LongDistanceMove;