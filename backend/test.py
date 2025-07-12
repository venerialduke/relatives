from typing import List, Tuple

DIRECTIONS = [
    (1, 0),   # E
    (1, -1),  # NE
    (0, -1),  # NW
    (-1, 0),  # W
    (-1, 1),  # SW
    (0, 1)    # SE
]

def hex_add(a, b):
    return (a[0] + b[0], a[1] + b[1])

def hex_scale(a, k):
    return (a[0] * k, a[1] * k)

def hex_ring(center, radius):
    results = []
    if radius == 0:
        return [center]
    
    # Start at direction 4 (SW), radius steps out
    q, r = hex_add(center, hex_scale(DIRECTIONS[4], radius))

    for i in range(6):
        for _ in range(radius):
            results.append((q, r))
            dq, dr = DIRECTIONS[i]
            q += dq
            r += dr
    return results

def hex_spiral(center, radius):
    results = [center]
    for k in range(1, radius + 1):
        results.extend(hex_ring(center, k))
    return results

def first_n_spiral_hexes(n):
    results = []
    radius = 0
    while len(results) < n:
        results.extend(hex_ring((0, 0), radius))
        radius += 1
    return results[:n]

print(first_n_spiral_hexes(15))