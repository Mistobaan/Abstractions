"""
Simplified Entity Component System using UML relationship types.

This module contains only essential data structures that cannot be computed from others.
All computed structures, helper methods, and complex logic have been removed.
Observer pattern support added for change tracking.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Set, Tuple, Type, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


# Observer pattern interfaces
class TreeObserver(Protocol):
    """Protocol for tree observers."""
    
    def notify(self, event: Any) -> None:
        """Handle a tree event."""
        ...


# UML-style edge types
class EdgeType(str, Enum):
    """UML relationship types between entities"""

    # UML Association types
    ASSOCIATION = "association"  # Simple association
    AGGREGATION = "aggregation"  # Has-a relationship (shared ownership)
    COMPOSITION = "composition"  # Part-of relationship (exclusive ownership)

    # Container specifications
    LIST_ITEM = "list_item"  # Item in ordered collection
    DICT_VALUE = "dict_value"  # Value in key-value mapping
    SET_MEMBER = "set_member"  # Member of unordered collection
    TUPLE_ITEM = "tuple_item"  # Item in fixed-size tuple


class EntityEdge(BaseModel):
    """Edge between two entities - essential fields only"""

    source_id: UUID
    target_id: UUID
    edge_type: EdgeType
    field_name: str

    # Container position (when applicable)
    container_index: Optional[int] = None  # For lists/tuples
    container_key: Optional[str] = None  # For dicts


class EntityTree(BaseModel):
    """Tree of entities - essential structure only"""

    model_config = {"arbitrary_types_allowed": True}

    # Identity
    root_ecs_id: UUID
    lineage_id: UUID

    # Core data structures
    nodes: Dict[UUID, "Entity"] = Field(default_factory=dict)
    edges: Dict[Tuple[UUID, UUID], EntityEdge] = Field(default_factory=dict)
    
    # Observer pattern (not serialized)
    observers: List[Any] = Field(default_factory=list, exclude=True)

    def find_entities_with_component(self, component_name: str) -> List[UUID]:
        """
        Find all entities that have a specific component.

        Args:
            component_name: Name of the component to search for

        Returns:
            List of entity IDs that have the specified component
        """
        return [
            entity_id
            for entity_id, entity in self.nodes.items()
            if component_name in entity.data
        ]

    def find_entities_by_relationship(
        self, source_id: UUID, edge_type: EdgeType
    ) -> List[UUID]:
        """
        Find entities connected by specific relationship types.

        Args:
            source_id: ID of the source entity
            edge_type: Type of relationship to search for

        Returns:
            List of target entity IDs connected to source by the specified edge type
        """
        return [
            target_id
            for (src_id, target_id), edge in self.edges.items()
            if src_id == source_id and edge.edge_type == edge_type
        ]
    
    def add_observer(self, observer: Any) -> None:
        """Add an observer."""
        if observer not in self.observers:
            self.observers.append(observer)
    
    def remove_observer(self, observer: Any) -> None:
        """Remove an observer."""
        if observer in self.observers:
            self.observers.remove(observer)
    
    def _notify_observers(self, event: Any) -> None:
        """Notify all observers of an event."""
        # Set the tree_id on the event
        if hasattr(event, 'tree_id'):
            event.tree_id = self.root_ecs_id
        
        for observer in self.observers:
            observer.notify(event)
    
    def add_node(self, entity: "Entity") -> None:
        """Add a node to the tree with observer notification."""
        if entity.ecs_id not in self.nodes:
            self.nodes[entity.ecs_id] = entity
            
            # Import here to avoid circular imports
            try:
                from ..change_tracking.events import NodeAddedEvent
                event = NodeAddedEvent(
                    entity_id=entity.ecs_id,
                    entity=entity,
                )
                self._notify_observers(event)
            except ImportError:
                pass  # Change tracking not available
    
    def remove_node(self, entity_id: UUID) -> Optional["Entity"]:
        """Remove a node from the tree with observer notification."""
        if entity_id in self.nodes:
            entity = self.nodes.pop(entity_id)
            
            # Import here to avoid circular imports
            try:
                from ..change_tracking.events import NodeRemovedEvent
                event = NodeRemovedEvent(
                    entity_id=entity_id,
                    entity=entity,
                    #tree_id=self.root_ecs_id
                )
                self._notify_observers(event)
            except ImportError:
                pass  # Change tracking not available
            
            return entity
        return None
    
    def add_edge(self, edge: EntityEdge) -> None:
        """Add an edge to the tree with observer notification."""
        edge_key = (edge.source_id, edge.target_id)
        if edge_key not in self.edges:
            self.edges[edge_key] = edge
            
            # Import here to avoid circular imports
            try:
                from ..change_tracking.events import EdgeAddedEvent
                event = EdgeAddedEvent(
                    edge_key=edge_key,
                    edge=edge,
                    # tree_id=self.root_ecs_id
                )
                self._notify_observers(event)
            except ImportError:
                pass  # Change tracking not available
    
    def remove_edge(self, source_id: UUID, target_id: UUID) -> Optional[EntityEdge]:
        """Remove an edge from the tree with observer notification."""
        edge_key = (source_id, target_id)
        if edge_key in self.edges:
            edge = self.edges.pop(edge_key)
            
            # Import here to avoid circular imports
            try:
                from ..change_tracking.events import EdgeRemovedEvent
                event = EdgeRemovedEvent(
                    edge_key=edge_key,
                    edge=edge,
                    #tree_id=self.root_ecs_id
                )
                self._notify_observers(event)
            except ImportError:
                pass  # Change tracking not available
            
            return edge
        return None


class Entity(BaseModel):
    """Core entity with essential fields only"""

    model_config = {"arbitrary_types_allowed": True}

    # Identity
    ecs_id: UUID = Field(default_factory=uuid4)
    lineage_id: UUID = Field(default_factory=uuid4)

    # Hierarchy
    root_ecs_id: Optional[UUID] = None

    # Versioning
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    previous_ecs_id: Optional[UUID] = None

    # Data
    data: Dict[str, Any] = Field(default_factory=dict)
    
    # Observer reference (not serialized)
    tree_ref: Optional["EntityTree"] = Field(default=None, exclude=True)
    
    def set_tree_reference(self, tree: "EntityTree") -> None:
        """Set reference to parent tree for observer notifications."""
        self.tree_ref = tree
    
    def add_component(self, name: str, value: Any) -> None:
        """Add a component with observer notification."""
        if name not in self.data:
            self.data[name] = value
            self._notify_component_added(name, value)
    
    def remove_component(self, name: str) -> Any:
        """Remove a component with observer notification."""
        if name in self.data:
            value = self.data.pop(name)
            self._notify_component_removed(name, value)
            return value
        return None
    
    def update_component(self, name: str, value: Any) -> None:
        """Update a component with observer notification."""
        if name in self.data:
            old_value = self.data[name]
            self.data[name] = value
            self._notify_component_modified(name, old_value, value)
        else:
            self.add_component(name, value)
    
    def _notify_component_added(self, name: str, value: Any) -> None:
        """Notify observers of component addition."""
        if self.tree_ref:
            try:
                from ..change_tracking.events import ComponentAddedEvent
                event = ComponentAddedEvent(
                    entity_id=self.ecs_id,
                    component_name=name,
                    component_value=value,
                    # tree_id=self.tree_ref.root_ecs_id
                )
                self.tree_ref._notify_observers(event)
            except ImportError:
                pass
    
    def _notify_component_removed(self, name: str, value: Any) -> None:
        """Notify observers of component removal."""
        if self.tree_ref:
            try:
                from ..change_tracking.events import ComponentRemovedEvent
                event = ComponentRemovedEvent(
                    entity_id=self.ecs_id,
                    component_name=name,
                    component_value=value,
                    # tree_id=self.tree_ref.root_ecs_id
                )
                self.tree_ref._notify_observers(event)
            except ImportError:
                pass
    
    def _notify_component_modified(self, name: str, old_value: Any, new_value: Any) -> None:
        """Notify observers of component modification."""
        if self.tree_ref:
            try:
                from ..change_tracking.events import ComponentModifiedEvent
                event = ComponentModifiedEvent(
                    entity_id=self.ecs_id,
                    component_name=name,
                    old_value=old_value,
                    new_value=new_value,
                    #tree_id=self.tree_ref.root_ecs_id
                )
                self.tree_ref._notify_observers(event)
            except ImportError:
                pass


# Global default entity tree for convenience functions
_default_tree: Optional[EntityTree] = None


def get_default_tree() -> EntityTree:
    """Get or create the default entity tree."""
    global _default_tree
    if _default_tree is None:
        # Create a default entity as root
        root_entity = Entity()
        _default_tree = EntityTree(
            root_ecs_id=root_entity.ecs_id, lineage_id=root_entity.lineage_id
        )
        _default_tree.nodes[root_entity.ecs_id] = root_entity
    return _default_tree


def set_default_tree(tree: EntityTree) -> None:
    """Set a custom default entity tree."""
    global _default_tree
    _default_tree = tree


def find_entities_with_component(
    component_name: str, tree: Optional[EntityTree] = None
) -> List[UUID]:
    """
    Find all entities that have a specific component in the tree.

    Args:
        component_name: Name of the component to search for
        tree: EntityTree to search in (uses default if None)

    Returns:
        List of entity IDs that have the specified component
    """
    if tree is None:
        tree = get_default_tree()
    return tree.find_entities_with_component(component_name)


def find_entities_by_relationship(
    source_id: UUID, edge_type: EdgeType, tree: Optional[EntityTree] = None
) -> List[UUID]:
    """
    Find entities connected by specific relationship types.

    Args:
        source_id: ID of the source entity
        edge_type: Type of relationship to search for
        tree: EntityTree to search in (uses default if None)

    Returns:
        List of target entity IDs connected to source by the specified edge type
    """
    if tree is None:
        tree = get_default_tree()
    return tree.find_entities_by_relationship(source_id, edge_type)


# Example entity types
class SimpleEntity(Entity):
    """Entity with direct field reference"""

    name: str = ""


class ContainerEntity(Entity):
    """Entity with container relationships"""

    items: List["Entity"] = Field(default_factory=list)
    mapping: Dict[str, "Entity"] = Field(default_factory=dict)
