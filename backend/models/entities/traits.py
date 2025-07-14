"""
Structure traits/mixins for providing common functionality across different structure types.
"""

from typing import Dict, Any
from abc import ABC, abstractmethod


class CollectionStructure(ABC):
    """
    Mixin/trait for structures that can accept resource deposits from autonomous units.
    Provides standardized deposit functionality for Factory, SpacePort, and other collection points.
    """
    
    def accept_deposit(self, resource_id: str, amount: int, depositor_unit=None) -> Dict[str, Any]:
        """
        Accept a resource deposit from an autonomous unit or other source.
        
        Args:
            resource_id: The ID of the resource being deposited
            amount: The amount of resource to deposit
            depositor_unit: The unit making the deposit (optional, for logging/tracking)
            
        Returns:
            Dict containing deposit result information
        """
        if amount <= 0:
            return {
                "success": False,
                "message": "Invalid deposit amount",
                "amount_deposited": 0
            }
        
        # Add resources to structure inventory
        current_amount = self.inventory.get(resource_id, 0)
        self.inventory[resource_id] = current_amount + amount
        
        # Log the deposit for tracking (optional)
        depositor_info = f" from {depositor_unit.id}" if depositor_unit else ""
        
        return {
            "success": True,
            "message": f"Deposited {amount} {resource_id}{depositor_info}",
            "amount_deposited": amount,
            "new_total": self.inventory[resource_id],
            "depositor": depositor_unit.id if depositor_unit else None
        }
    
    def is_collection_point(self) -> bool:
        """
        Identify this structure as a valid collection point for autonomous units.
        
        Returns:
            True, indicating this structure accepts deposits
        """
        return True
    
    def get_collection_capacity(self, resource_id: str) -> Dict[str, Any]:
        """
        Get information about collection capacity for a specific resource.
        Override in subclasses to implement capacity limits.
        
        Args:
            resource_id: The resource to check capacity for
            
        Returns:
            Dict with capacity information
        """
        return {
            "has_capacity_limit": False,
            "current_amount": self.inventory.get(resource_id, 0),
            "max_capacity": None,  # Unlimited by default
            "remaining_capacity": None  # Unlimited by default
        }
    
    def can_accept_deposit(self, resource_id: str, amount: int) -> Dict[str, Any]:
        """
        Check if this structure can accept a deposit of the specified resource and amount.
        
        Args:
            resource_id: The resource to check
            amount: The amount to potentially deposit
            
        Returns:
            Dict indicating whether deposit is possible
        """
        if amount <= 0:
            return {
                "can_accept": False,
                "reason": "Invalid amount"
            }
        
        capacity_info = self.get_collection_capacity(resource_id)
        
        # If there's no capacity limit, accept anything
        if not capacity_info["has_capacity_limit"]:
            return {
                "can_accept": True,
                "reason": "No capacity limit"
            }
        
        # Check against capacity limit
        remaining = capacity_info["remaining_capacity"]
        if remaining is not None and amount > remaining:
            return {
                "can_accept": False,
                "reason": f"Insufficient capacity (need {amount}, have {remaining})"
            }
        
        return {
            "can_accept": True,
            "reason": "Within capacity limits"
        }


class AdvancedCollectionStructure(CollectionStructure):
    """
    Extended collection structure with additional features like capacity limits,
    processing bonuses, and selective resource acceptance.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize collection-specific attributes if not already present
        if not hasattr(self, 'collection_capacity_limits'):
            self.collection_capacity_limits = {}  # Dict[resource_id, max_amount]
        if not hasattr(self, 'accepted_resources'):
            self.accepted_resources = None  # None = accept all, List = specific resources only
        if not hasattr(self, 'processing_bonuses'):
            self.processing_bonuses = {}  # Dict[resource_id, multiplier]
    
    def get_collection_capacity(self, resource_id: str) -> Dict[str, Any]:
        """
        Get capacity information with support for per-resource limits.
        """
        max_capacity = self.collection_capacity_limits.get(resource_id)
        current_amount = self.inventory.get(resource_id, 0)
        
        if max_capacity is not None:
            return {
                "has_capacity_limit": True,
                "current_amount": current_amount,
                "max_capacity": max_capacity,
                "remaining_capacity": max_capacity - current_amount
            }
        
        return super().get_collection_capacity(resource_id)
    
    def can_accept_resource_type(self, resource_id: str) -> bool:
        """
        Check if this structure accepts deposits of a specific resource type.
        
        Args:
            resource_id: The resource type to check
            
        Returns:
            True if resource type is accepted
        """
        # If no restriction list, accept all resources
        if self.accepted_resources is None:
            return True
        
        # Check if resource is in the accepted list
        return resource_id in self.accepted_resources
    
    def accept_deposit(self, resource_id: str, amount: int, depositor_unit=None) -> Dict[str, Any]:
        """
        Enhanced deposit with resource type checking and processing bonuses.
        """
        # Check if resource type is accepted
        if not self.can_accept_resource_type(resource_id):
            return {
                "success": False,
                "message": f"Structure does not accept {resource_id}",
                "amount_deposited": 0
            }
        
        # Check capacity
        capacity_check = self.can_accept_deposit(resource_id, amount)
        if not capacity_check["can_accept"]:
            return {
                "success": False,
                "message": f"Cannot accept deposit: {capacity_check['reason']}",
                "amount_deposited": 0
            }
        
        # Apply processing bonus if available
        processing_multiplier = self.processing_bonuses.get(resource_id, 1.0)
        actual_amount = int(amount * processing_multiplier)
        
        # Perform the deposit
        result = super().accept_deposit(resource_id, actual_amount, depositor_unit)
        
        # Add bonus information to result
        if processing_multiplier != 1.0:
            result["processing_bonus"] = processing_multiplier
            result["original_amount"] = amount
            result["message"] += f" (with {processing_multiplier}x bonus)"
        
        return result