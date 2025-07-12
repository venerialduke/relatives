
export const HEX_RADIUS = 20;
export const HEX_WIDTH = Math.sqrt(3) * HEX_RADIUS;
export const HEX_HEIGHT = 2 * HEX_RADIUS;
export const DIRECTION_ANGLES = [0, -60, -120, 180, 120, 60];

export const axialToPixel = (q, r) => [
  1000 + HEX_WIDTH * (q + r / 2),
  1600 + HEX_HEIGHT * (r * 3 / 4)
];

export const drawHex = (cx, cy) => {
  return Array.from({ length: 6 }, (_, i) => {
    const angle = (Math.PI / 3) * i + Math.PI / 6;
    const x = cx + HEX_RADIUS * Math.cos(angle);
    const y = cy + HEX_RADIUS * Math.sin(angle);
    return `${x},${y}`;
  }).join(" ");
};