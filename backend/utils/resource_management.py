from typing import Dict

def update_quantity_map(
	target: Dict[str, int],
	changes: Dict[str, int]
) -> None:
	"""
	Modifies `target` in-place using the delta values in `changes`.
	Removes entries that drop to zero or below.
	"""
	for key, delta in changes.items():
		target[key] = target.get(key, 0) + delta
		if target[key] <= 0:
			del target[key]
			
class InventoryMixin:
	def update_inventory(self, inventory_change: Dict[str, int]):
		update_quantity_map(self.inventory, inventory_change)