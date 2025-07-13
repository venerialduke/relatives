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

  const handleBodySelect = (body) => {
    setSelectedBody(body);
    setSelectedSpace(null);
  };

  const handleSpaceSelect = (space) => {
    setSelectedSpace(space);
    setShowConfirmation(true);
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

  const canAfford = movementOptions && movementOptions.current_fuel >= movementOptions.inter_body_cost;

  if (!isVisible) return null;

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
              <span className={`fuel-amount ${canAfford ? 'sufficient' : 'insufficient'}`}>
                Fuel: {movementOptions.current_fuel} / {movementOptions.inter_body_cost} needed
              </span>
            </div>

            {!canAfford && (
              <div className="warning-message">
                Insufficient fuel for inter-body movement. You need at least {movementOptions.inter_body_cost} fuel.
              </div>
            )}

            {movementOptions.reachable_bodies.length === 0 ? (
              <div className="no-destinations">
                No explored destinations available on other bodies.
              </div>
            ) : (
              <div className="bodies-grid">
                {movementOptions.reachable_bodies.map((body) => (
                  <div 
                    key={body.body_id} 
                    className={`body-card ${selectedBody?.body_id === body.body_id ? 'selected' : ''} ${canAfford ? 'affordable' : 'unaffordable'}`}
                    onClick={() => canAfford && handleBodySelect(body)}
                  >
                    <div className="body-header">
                      <h4>{body.name}</h4>
                      <span className="fuel-cost">Cost: {body.fuel_cost} fuel</span>
                    </div>
                    <div className="explored-count">
                      {body.explored_spaces.length} explored space(s)
                    </div>
                  </div>
                ))}
              </div>
            )}

            {selectedBody && (
              <div className="spaces-section">
                <h4>Select destination on {selectedBody.name}:</h4>
                <div className="spaces-grid">
                  {selectedBody.explored_spaces.map((space) => (
                    <div 
                      key={space.space_id}
                      className="space-card"
                      onClick={() => handleSpaceSelect(space)}
                    >
                      <div className="space-name">{space.name}</div>
                      {space.named_inventory && Object.keys(space.named_inventory).length > 0 && (
                        <div className="space-resources">
                          {Object.entries(space.named_inventory).slice(0, 3).map(([resource, amount]) => (
                            <span key={resource} className="resource-tag">
                              {resource}: {amount}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
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
              <p>This will cost <strong>{movementOptions.inter_body_cost} fuel</strong></p>
              <p>Remaining fuel: <strong>{movementOptions.current_fuel - movementOptions.inter_body_cost}</strong></p>
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