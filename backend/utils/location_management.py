from typing import Tuple, Union

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


