"""
Core types and enums for change tracking.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Tuple
from uuid import UUID


class ChangeType(str, Enum):
    """Types of changes that can occur in an EntityTree."""
    
    # Node changes
    NODE_ADDED = "node_added"
    NODE_REMOVED = "node_removed"
    NODE_MODIFIED = "node_modified"
    
    # Edge changes
    EDGE_ADDED = "edge_added"
    EDGE_REMOVED = "edge_removed"
    EDGE_MODIFIED = "edge_modified"
    
    # Component changes
    COMPONENT_ADDED = "component_added"
    COMPONENT_REMOVED = "component_removed"
    COMPONENT_MODIFIED = "component_modified"


@dataclass
class TreeChange:
    """Represents a single change in an EntityTree."""
    
    change_type: ChangeType
    entity_id: Optional[UUID] = None
    edge_key: Optional[Tuple[UUID, UUID]] = None
    component_name: Optional[str] = None
    old_value: Any = None
    new_value: Any = None
    details: Dict[str, Any] = None
    timestamp: Optional[float] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}