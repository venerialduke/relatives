from typing import Tuple, Union, List

def hex_distance(a: Tuple[int, int], b: Tuple[int, int]) -> int:
	"""
	Returns the hex distance between two axial coordinates.
	"""
	q1, r1 = a
	q2, r2 = b
	return max(abs(q1 - q2), abs(r1 - r2), abs((-q1 - r1) - (-q2 - r2)))

def are_adjacent_coords(a: Tuple[int, int], b: Tuple[int, int]) -> bool:
	"""
	Returns True if the two axial coordinates are adjacent.
	"""
	return hex_distance(a, b) == 1

def space_distance(s1,s2):
	return hex_distance((s1.q, s1.r), (s2.q, s2.r))

def are_adjacent_spaces(s1, s2) -> bool:
	"""
	Returns True if two Space-like objects with .q and .r attributes are adjacent.
	"""
	return space_distance(s1,s2) == 1

def estimate_body_radius(space_count):
	# Inverse of: 1 + 3*r*(r-1)
	# Use a simple lookup or solve quadratic
	r = 1
	while 1 + 3 * r * (r - 1) < space_count:
		r += 1
	return r


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
