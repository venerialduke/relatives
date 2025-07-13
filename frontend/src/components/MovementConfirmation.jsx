import React, { useState } from 'react';

function MovementConfirmation({ 
  isVisible, 
  targetSpace, 
  movementInfo, 
  playerUnit, 
  onConfirm, 
  onCancel 
}) {
  const [loading, setLoading] = useState(false);

  if (!isVisible || !targetSpace || !movementInfo) return null;

  const handleConfirm = async () => {
    setLoading(true);
    try {
      await onConfirm();
    } finally {
      setLoading(false);
    }
  };

  const canAfford = playerUnit?.named_inventory?.Fuel >= movementInfo.cost;
  const remainingFuel = (playerUnit?.named_inventory?.Fuel || 0) - movementInfo.cost;

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
      <div className="movement-confirmation-modal" style={{
        backgroundColor: '#1a1a1a',
        borderRadius: '12px',
        padding: '24px',
        minWidth: '300px',
        maxWidth: '400px',
        boxShadow: '0 8px 32px rgba(0, 255, 255, 0.3)',
        border: '2px solid #00ffff',
        color: '#ffffff'
      }}>
        <div className="modal-header" style={{ marginBottom: '16px' }}>
          <h3 style={{ margin: 0, color: '#ffffff' }}>Confirm Movement</h3>
        </div>

        <div className="movement-details" style={{ marginBottom: '20px' }}>
          <p style={{ margin: '8px 0', fontSize: '16px' }}>
            <strong>Destination:</strong> {targetSpace.name}
          </p>
          
          <p style={{ margin: '8px 0', fontSize: '14px', color: '#cccccc' }}>
            <strong>Body:</strong> {movementInfo.bodyName}
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
              {movementInfo.icon}
            </span>
            <div>
              <div style={{ fontSize: '14px', fontWeight: 'bold' }}>
                {movementInfo.travelType}
              </div>
              <div style={{ fontSize: '12px', color: '#cccccc' }}>
                {movementInfo.description}
              </div>
            </div>
          </div>

          <div style={{ 
            padding: '12px',
            backgroundColor: canAfford ? 'rgba(40, 167, 69, 0.2)' : 'rgba(220, 53, 69, 0.2)',
            borderRadius: '6px',
            border: `1px solid ${canAfford ? '#28a745' : '#dc3545'}`
          }}>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              marginBottom: '4px'
            }}>
              <span>Fuel Cost:</span>
              <span style={{ fontWeight: 'bold' }}>{movementInfo.cost}</span>
            </div>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              marginBottom: '4px'
            }}>
              <span>Current Fuel:</span>
              <span>{playerUnit?.named_inventory?.Fuel || 0}</span>
            </div>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              fontWeight: 'bold',
              borderTop: '1px solid #555',
              paddingTop: '4px'
            }}>
              <span>Remaining:</span>
              <span style={{ color: canAfford ? '#28a745' : '#dc3545' }}>
                {remainingFuel}
              </span>
            </div>
          </div>

          {!canAfford && (
            <div style={{
              marginTop: '12px',
              padding: '8px',
              backgroundColor: 'rgba(220, 53, 69, 0.2)',
              color: '#dc3545',
              borderRadius: '4px',
              fontSize: '14px'
            }}>
              ⚠️ Insufficient fuel! Need {movementInfo.cost - (playerUnit?.named_inventory?.Fuel || 0)} more fuel.
            </div>
          )}
        </div>

        <div className="modal-buttons" style={{
          display: 'flex',
          gap: '12px',
          justifyContent: 'flex-end'
        }}>
          <button
            onClick={onCancel}
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
            onClick={handleConfirm}
            disabled={!canAfford || loading}
            style={{
              padding: '8px 16px',
              borderRadius: '6px',
              border: 'none',
              backgroundColor: canAfford ? '#007bff' : '#6c757d',
              color: 'white',
              cursor: canAfford ? 'pointer' : 'not-allowed',
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

export default MovementConfirmation;