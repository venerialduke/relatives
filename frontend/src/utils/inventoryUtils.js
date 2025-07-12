export function summarizeInventory(inventory) {
  const summary = {};
  for (const item of inventory || []) {
    summary[item] = (summary[item] || 0) + 1;
  }
  return summary;
}

export function canBuildStructure(unit, requirements) {
  if (!unit || !unit.inventory_summary) return false;

  for (const [resource, amount] of Object.entries(requirements)) {
    if ((unit.inventory_summary[resource] || 0) < amount) {
      return false;
    }
  }
  return true;
}