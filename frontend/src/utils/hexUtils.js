// src/utils/hexUtils.js

export const HEX_RADIUS = 20;
export const HEX_WIDTH = Math.sqrt(3) * HEX_RADIUS;
export const HEX_HEIGHT = 2 * HEX_RADIUS;

export const HEX_DIRECTIONS = [
  [1, 0],  [1, -1],  [0, -1],
  [-1, 0], [-1, 1],  [0, 1]
];

export const polarToCartesian = (angle, radius) => [
  Math.cos(angle) * radius,
  Math.sin(angle) * radius
];

// Real hex grid coordinates (offset layout)
export const generateHexCoordinates = (count) => {
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
