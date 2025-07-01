import React, { useEffect, useState } from 'react';
import './App.css';

const HEX_RADIUS = 20;
const HEX_WIDTH = Math.sqrt(3) * HEX_RADIUS;
const HEX_HEIGHT = 2 * HEX_RADIUS;

const polarToCartesian = (angle, radius) => [
	Math.cos(angle) * radius,
	Math.sin(angle) * radius
];

// Real hex grid coordinates (offset layout)
const generateHexCoordinates = (count) => {
	const coords = [];
	let layers = 0;

	while (3 * layers * (layers + 1) + 1 < count) {
		layers++;
	}

	let placed = 0;
	for (let q = -layers; q <= layers; q++) {
		for (let r = -layers; r <= layers; r++) {
			const s = -q - r;
			if (Math.abs(s) > layers) continue;

			const x = HEX_WIDTH * (q + r / 2);
			const y = HEX_HEIGHT * (r * 3 / 4);

			coords.push([x, y]);
			placed++;
			if (placed >= count) return coords;
		}
	}
	return coords;
};

function App() {
	const [system, setSystem] = useState(null);
	const [unit, setUnit] = useState(null);
	const [selectedSpace, setSelectedSpace] = useState(null);
	const [message, setMessage] = useState('');

  const centerX = 600;
  const centerY = 500;  // was 400 — increased to push map downward


	useEffect(() => {
		fetch('/api/system')
			.then(res => res.json())
			.then(data => setSystem(data));

		fetch('/api/unit')
			.then(res => res.json())
			.then(data => {
			setUnit({
				...data,
				inventory_summary: summarizeInventory(data.inventory)
			});});
	}, []);

	const moveUnit = (spaceId) => {
		fetch('/api/move_unit', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ space_id: spaceId })
		})
			.then(res => res.json())
			.then(data => {
			setUnit({
				...data,
				inventory_summary: summarizeInventory(data.inventory)
			});});
	};

	const collectItem = (item) => {
		fetch('/api/collect_item', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ item })
		})
			.then(res => res.json())
			.then(data => {
			setUnit({
				...data,
				inventory_summary: summarizeInventory(data.inventory)
			});});
	};

	const buildBuilding = (building) => {
		fetch('/api/build_building', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ building })
		})
			.then(res => res.json())
			.then(data => {
				if (data.error) setMessage(data.error);
				else {
					setUnit(data.unit);
					fetch('/api/system').then(res => res.json()).then(setSystem);
					setMessage(`${building} built!`);
				}
			});
	};

	const textLabel = (text, x, y, size = '12px', color = 'black') =>
		text ? <text x={x} y={y} textAnchor="middle" fontSize={size} fill={color}>{text}</text> : null;

	const renderHex = (x, y, space, isCurrent) => (
		<g
			key={space.id}
			transform={`translate(${x},${y})`}
			onContextMenu={(e) => {
				e.preventDefault();
				setSelectedSpace(space);
				moveUnit(space.id);
			}}
		>
			<polygon
				points={Array.from({ length: 6 }, (_, i) => {
					const angle = Math.PI / 3 * i + Math.PI / 6;
					const px = HEX_RADIUS * Math.cos(angle);
					const py = HEX_RADIUS * Math.sin(angle);
					return `${px},${py}`;
				}).join(' ')}
				fill={isCurrent ? 'lightgreen' : '#ddd'}
				stroke="#333"
			/>
			{textLabel(space.building, 0, 0, '8px', 'blue')}
		</g>
	);

	const inventoryMap = unit?.inventory?.reduce((acc, item) => {
		acc[item] = (acc[item] || 0) + 1;
		return acc;
	}, {}) || {};

  const canBuild = (buildingName, requirements) => {
    if (!unit || !unit.inventory_summary) return false;

    for (const [resource, amount] of Object.entries(requirements)) {
      if ((unit.inventory_summary[resource] || 0) < amount) {
        return false;
      }
    }
    return true;
  };


  const summarizeInventory = (inventory) => {
    const summary = {};
    for (const item of inventory || []) {
      summary[item] = (summary[item] || 0) + 1;
    }
    return summary;
  };


  return (
    <div className="main-container">
      <div className="map-container">
        <h1>Explore: {system?.name}</h1>
        <svg width="1200" height="1200">
          <circle cx={centerX} cy={centerY} r={30} fill="orange" />
          {textLabel('Sun', centerX, centerY - 5)}

          {system?.bodies.map((body, bIdx) => {
            const angle = (bIdx / system.bodies.length) * 2 * Math.PI;
            const baseRadius = 300 + body.spaces.length;
            const [bx, by] = polarToCartesian(angle, baseRadius);
            const hexCoords = generateHexCoordinates(body.spaces.length);

            return (
              <g key={body.id} transform={`translate(${centerX + bx},${centerY + by})`}>
                <circle r={5} fill="gray" />
                {textLabel(body.name, 0, -HEX_RADIUS * 4, '14px', 'black')}
                {body.spaces.map((space, sIdx) => {
                  const [dx, dy] = hexCoords[sIdx];
                  const isCurrent = unit?.current_space_id === space.id;
                  return renderHex(dx, dy, space, isCurrent);
                })}
              </g>
            );
          })}
        </svg>
      </div>

      <div className="sidebar">
        <h2>Inventory</h2>
        <ul>
          {Object.entries(unit?.inventory_summary || {}).map(([item, count]) => (
            <li key={item}>{item} x{count}</li>
          ))}
        </ul>

        {selectedSpace && (
          <>
            <h2>{selectedSpace.name}</h2>
            {selectedSpace.items.length > 0 ? (
              <div>
                <p>Resources:</p>
                <ul>
                  {selectedSpace.items.map(item => (
                    <li key={item}>
                      {item} <button onClick={() => collectItem(item)}>Collect</button>
                    </li>
                  ))}
                </ul>
              </div>
            ) : <p>No items left</p>}

            <h3>Build Options</h3>
            <ul>
              {Object.entries({
                Collector: { Silver: 2, Ore: 1 },
                Factory: { Algae: 2, SpaceDust: 3 },
                Settlement: { Fungus: 4 }
              }).map(([name, reqs]) => {
                const inv = unit?.inventory || [];
                return (
                  <li key={name}>
                    {name}{' '}
                    {canBuild(name, reqs) ? (
                      <button onClick={() => buildBuilding(name)}>Build</button>
                    ) : (
                      <span style={{ color: 'gray' }}>
                        (
                        {Object.entries(reqs).map(([res, count]) => {
                          const have = inv.filter(i => i === res).length;
                          const need = count - have;
                          return `${res} x${count}${need > 0 ? ` – need ${need}` : ''}`;
                        }).join(', ')}
                        )
                      </span>
                    )}
                  </li>
                );
              })}
            </ul>
            <p>{message}</p>
          </>
        )}
      </div>
    </div>
  );

}

export default App;
