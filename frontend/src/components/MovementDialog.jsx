import React, { useState, useEffect, useCallback } from 'react';

function MovementDialog({ 
  isVisible, 
  onClose, 
  onMoveComplete, 
  playerUnit,
  targetSpace = null  // If provided, show cost for specific target
}) {
  const [destinations, setDestinations] = useState([]);
  const [selectedDestination, setSelectedDestination] = useState(null);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentFuel, setCurrentFuel] = useState(0);

  const fetchMovementDestinations = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`/api/movement_destinations?unit_id=${encodeURIComponent(playerUnit.id)}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch movement destinations');
      }
      
      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      setDestinations(data.destinations || []);
      setCurrentFuel(data.current_fuel || 0);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [playerUnit]);

  const fetchMovementCost = useCallback(async (targetSpaceId) => {
    try {
      setLoading(true);
      setError(null);
      
      const url = `/api/movement_cost?unit_id=${encodeURIComponent(playerUnit.id)}&target_space_id=${encodeURIComponent(targetSpaceId)}`;
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error('Failed to fetch movement cost');
      }
      
      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      // Convert single target to destination format
      const destination = {
        space_id: targetSpaceId,
        space_name: targetSpace.name,
        body_name: data.body_name,
        cost: data.cost,
        movement_type: data.movement_type,
        description: data.description,
        icon: data.icon,
        can_afford: data.can_afford,
        is_valid: data.is_valid
      };
      
      setSelectedDestination(destination);
      setCurrentFuel(data.current_fuel);
      setShowConfirmation(true);
      
      if (!data.is_valid) {
        setError(data.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [playerUnit, targetSpace]);

  useEffect(() => {
    if (isVisible && playerUnit) {
      if (targetSpace) {
        // Single target mode - calculate cost for specific target
        fetchMovementCost(targetSpace.id);
      } else {
        // Destination selection mode - fetch all available destinations
        fetchMovementDestinations();
      }
    }
  }, [isVisible, playerUnit, targetSpace, fetchMovementCost, fetchMovementDestinations]);

  const handleDestinationSelect = (destination) => {
    if (!destination.can_afford) return;
    setSelectedDestination(destination);
    setShowConfirmation(true);
  };

  const confirmMove = async () => {
    if (!selectedDestination) return;

    try {
      setLoading(true);
      const response = await fetch('/api/move_unit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          unit_id: playerUnit.id,
          direction: null,
          space_id: selectedDestination.space_id
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
    setDestinations([]);
    setSelectedDestination(null);
    setShowConfirmation(false);
    setError(null);
    onClose();
  };

  const handleBack = () => {
    setSelectedDestination(null);
    setShowConfirmation(false);
    setError(null);
  };

  if (!isVisible) return null;

  // Confirmation mode
  if (showConfirmation && selectedDestination) {
    const remainingFuel = currentFuel - selectedDestination.cost;
    
    return (
      <div className="modal-overlay" style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000
      }}>
        <div className="movement-dialog-modal" style={{
          backgroundColor: '#1a1a1a',
          borderRadius: '12px',
          padding: '24px',
          minWidth: '350px',
          maxWidth: '450px',
          boxShadow: '0 8px 32px rgba(0, 255, 255, 0.3)',
          border: '2px solid #00ffff',
          color: '#ffffff'
        }}>
          <div className="modal-header" style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            marginBottom: '16px' 
          }}>
            <h3 style={{ margin: 0, color: '#ffffff' }}>Confirm Movement</h3>
            <button onClick={handleClose} style={{
              background: 'none',
              border: 'none',
              color: '#ffffff',
              fontSize: '24px',
              cursor: 'pointer'
            }}>×</button>
          </div>

          <div className="movement-details" style={{ marginBottom: '20px' }}>
            <p style={{ margin: '8px 0', fontSize: '16px' }}>
              <strong>Destination:</strong> {selectedDestination.space_name}
            </p>
            
            <p style={{ margin: '8px 0', fontSize: '14px', color: '#cccccc' }}>
              <strong>Body:</strong> {selectedDestination.body_name}
            </p>

            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              margin: '12px 0',
              padding: '8px',
              backgroundColor: '#2a2a2a',
              borderRadius: '6px'
            }}>
              <span style={{ marginRight: '8px', fontSize: '18px' }}>
                {selectedDestination.icon}
              </span>
              <div>
                <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
                  {selectedDestination.movement_type === 'same_body' ? 'Same Body Travel' :
                   selectedDestination.movement_type === 'space_port' ? 'Space Port Network' :
                   'Inter-body Travel'}
                </div>
                <div style={{ fontSize: '12px', color: '#cccccc' }}>
                  {selectedDestination.description}
                </div>
              </div>
            </div>

            <div style={{ 
              padding: '12px',
              backgroundColor: selectedDestination.can_afford ? 'rgba(40, 167, 69, 0.2)' : 'rgba(220, 53, 69, 0.2)',
              borderRadius: '6px',
              border: `1px solid ${selectedDestination.can_afford ? '#28a745' : '#dc3545'}`
            }}>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                marginBottom: '4px'
              }}>
                <span>Fuel Cost:</span>
                <span style={{ fontWeight: 'bold' }}>{selectedDestination.cost}</span>
              </div>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                marginBottom: '4px'
              }}>
                <span>Current Fuel:</span>
                <span>{currentFuel}</span>
              </div>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                fontWeight: 'bold',
                borderTop: '1px solid #555',
                paddingTop: '4px'
              }}>
                <span>Remaining:</span>
                <span style={{ color: selectedDestination.can_afford ? '#28a745' : '#dc3545' }}>
                  {remainingFuel}
                </span>
              </div>
            </div>

            {!selectedDestination.can_afford && (
              <div style={{
                marginTop: '12px',
                padding: '8px',
                backgroundColor: 'rgba(220, 53, 69, 0.2)',
                color: '#dc3545',
                borderRadius: '4px',
                fontSize: '14px'
              }}>
                ⚠️ Insufficient fuel! Need {selectedDestination.cost - currentFuel} more fuel.
              </div>
            )}

            {error && (
              <div style={{
                marginTop: '12px',
                padding: '8px',
                backgroundColor: 'rgba(220, 53, 69, 0.2)',
                color: '#dc3545',
                borderRadius: '4px',
                fontSize: '14px'
              }}>
                ⚠️ {error}
              </div>
            )}
          </div>

          <div className="modal-buttons" style={{
            display: 'flex',
            gap: '12px',
            justifyContent: 'flex-end'
          }}>
            {!targetSpace && (
              <button
                onClick={handleBack}
                disabled={loading}
                style={{
                  padding: '8px 16px',
                  borderRadius: '6px',
                  backgroundColor: '#2a2a2a',
                  color: '#ffffff',
                  border: '1px solid #555',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                Back
              </button>
            )}
            <button
              onClick={handleClose}
              disabled={loading}
              style={{
                padding: '8px 16px',
                borderRadius: '6px',
                backgroundColor: '#2a2a2a',
                color: '#ffffff',
                border: '1px solid #555',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              Cancel
            </button>
            <button
              onClick={confirmMove}
              disabled={!selectedDestination.can_afford || loading || error}
              style={{
                padding: '8px 16px',
                borderRadius: '6px',
                border: 'none',
                backgroundColor: selectedDestination.can_afford && !error ? '#007bff' : '#6c757d',
                color: 'white',
                cursor: selectedDestination.can_afford && !error ? 'pointer' : 'not-allowed',
                fontSize: '14px',
                opacity: loading ? 0.7 : 1
              }}
            >
              {loading ? 'Moving...' : 'Confirm Move'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Destination selection mode
  return (
    <div className="modal-overlay" style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div className="movement-dialog-modal" style={{
        backgroundColor: '#1a1a1a',
        borderRadius: '12px',
        padding: '24px',
        minWidth: '400px',
        maxWidth: '600px',
        maxHeight: '80vh',
        overflow: 'hidden',
        boxShadow: '0 8px 32px rgba(0, 255, 255, 0.3)',
        border: '2px solid #00ffff',
        color: '#ffffff',
        display: 'flex',
        flexDirection: 'column'
      }}>
        <div className="modal-header" style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: '16px' 
        }}>
          <h3 style={{ margin: 0, color: '#ffffff' }}>Movement Destinations</h3>
          <button onClick={handleClose} style={{
            background: 'none',
            border: 'none',
            color: '#ffffff',
            fontSize: '24px',
            cursor: 'pointer'
          }}>×</button>
        </div>

        {loading && (
          <div style={{ textAlign: 'center', padding: '20px' }}>
            Loading destinations...
          </div>
        )}

        {error && (
          <div style={{
            marginBottom: '16px',
            padding: '8px',
            backgroundColor: 'rgba(220, 53, 69, 0.2)',
            color: '#dc3545',
            borderRadius: '4px',
            fontSize: '14px'
          }}>
            ⚠️ {error}
          </div>
        )}

        {!loading && !error && (
          <div className="modal-body" style={{ flex: 1, overflow: 'hidden' }}>
            <div className="fuel-status" style={{ marginBottom: '16px' }}>
              <span style={{ color: '#cccccc' }}>
                Available Fuel: <strong>{currentFuel}</strong>
              </span>
            </div>

            {destinations.length === 0 ? (
              <div style={{ textAlign: 'center', color: '#cccccc', padding: '20px' }}>
                No destinations available. Explore more spaces to unlock travel options.
              </div>
            ) : (
              <div style={{ 
                maxHeight: '400px', 
                overflowY: 'auto',
                paddingRight: '8px'
              }}>
                {destinations.map((destination) => (
                  <div 
                    key={destination.space_id}
                    onClick={() => destination.can_afford && handleDestinationSelect(destination)}
                    style={{ 
                      cursor: destination.can_afford ? 'pointer' : 'not-allowed',
                      border: '2px solid #555',
                      borderRadius: '8px',
                      padding: '12px',
                      margin: '8px 0',
                      backgroundColor: destination.can_afford ? '#2a2a2a' : '#1a1a1a',
                      transition: 'all 0.2s ease',
                      opacity: destination.can_afford ? 1 : 0.6
                    }}
                    onMouseEnter={(e) => {
                      if (destination.can_afford) {
                        e.target.style.borderColor = '#00ffff';
                        e.target.style.backgroundColor = '#333333';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (destination.can_afford) {
                        e.target.style.borderColor = '#555';
                        e.target.style.backgroundColor = '#2a2a2a';
                      }
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                          <span style={{ marginRight: '8px', fontSize: '16px' }}>
                            {destination.icon}
                          </span>
                          <div>
                            <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
                              {destination.space_name}
                            </div>
                            <div style={{ fontSize: '12px', color: '#cccccc' }}>
                              {destination.body_name}
                            </div>
                          </div>
                        </div>
                        <div style={{ fontSize: '12px', color: '#cccccc', marginLeft: '24px' }}>
                          {destination.description}
                        </div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ 
                          fontSize: '14px', 
                          fontWeight: 'bold',
                          color: destination.can_afford ? '#28a745' : '#dc3545'
                        }}>
                          {destination.cost} fuel
                        </div>
                        {!destination.can_afford && (
                          <div style={{ fontSize: '11px', color: '#dc3545' }}>
                            Need {destination.cost - currentFuel} more
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default MovementDialog;