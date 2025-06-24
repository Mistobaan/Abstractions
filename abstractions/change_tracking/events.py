"""
Event classes for the observer pattern in change tracking.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
from uuid import UUID

from ..ecs.entity import Entity, EntityEdge


class TreeEvent(ABC):
    """Base class for all tree events."""
    
    def __init__(self):
        self.timestamp = datetime.now(timezone.utc)
        self.tree_id: Optional[UUID] = None


@dataclass
class NodeAddedEvent(TreeEvent):
    """Event fired when a node is added to the tree."""
    
    entity_id: UUID
    entity: Entity
    
    def __post_init__(self):
        super().__init__()


@dataclass
class NodeRemovedEvent(TreeEvent):
    """Event fired when a node is removed from the tree."""
    
    entity_id: UUID
    entity: Entity
    
    def __post_init__(self):
        super().__init__()


@dataclass
class NodeModifiedEvent(TreeEvent):
    """Event fired when a node is modified."""
    
    entity_id: UUID
    entity: Entity
    field_name: str
    old_value: Any
    new_value: Any
    
    def __post_init__(self):
        super().__init__()


@dataclass
class EdgeAddedEvent(TreeEvent):
    """Event fired when an edge is added to the tree."""
    
    edge_key: Tuple[UUID, UUID]
    edge: EntityEdge
    
    def __post_init__(self):
        super().__init__()


@dataclass
class EdgeRemovedEvent(TreeEvent):
    """Event fired when an edge is removed from the tree."""
    
    edge_key: Tuple[UUID, UUID]
    edge: EntityEdge
    
    def __post_init__(self):
        super().__init__()


@dataclass
class EdgeModifiedEvent(TreeEvent):
    """Event fired when an edge is modified."""
    
    edge_key: Tuple[UUID, UUID]
    old_edge: EntityEdge
    new_edge: EntityEdge
    
    def __post_init__(self):
        super().__init__()


@dataclass
class ComponentAddedEvent(TreeEvent):
    """Event fired when a component is added to an entity."""
    
    entity_id: UUID
    component_name: str
    component_value: Any
    
    def __post_init__(self):
        super().__init__()


@dataclass
class ComponentRemovedEvent(TreeEvent):
    """Event fired when a component is removed from an entity."""
    
    entity_id: UUID
    component_name: str
    component_value: Any
    
    def __post_init__(self):
        super().__init__()


@dataclass
class ComponentModifiedEvent(TreeEvent):
    """Event fired when a component is modified in an entity."""
    
    entity_id: UUID
    component_name: str
    old_value: Any
    new_value: Any
    
    def __post_init__(self):
        super().__init__()