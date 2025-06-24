"""
Simplified Entity Component System using UML relationship types.

This module contains only essential data structures that cannot be computed from others.
All computed structures, helper methods, and complex logic have been removed.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Type, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


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

    # Identity
    root_ecs_id: UUID
    lineage_id: UUID

    # Core data structures
    nodes: Dict[UUID, "Entity"] = Field(default_factory=dict)
    edges: Dict[Tuple[UUID, UUID], EntityEdge] = Field(default_factory=dict)

    def find_entities_with_component(self, component_name: str) -> List[UUID]:
        """
        Find all entities that have a specific component.
        
        Args:
            component_name: Name of the component to search for
            
        Returns:
            List of entity IDs that have the specified component
        """
        return [
            entity_id for entity_id, entity in self.nodes.items()
            if component_name in entity.data
        ]

    def find_entities_by_relationship(self, source_id: UUID, edge_type: EdgeType) -> List[UUID]:
        """
        Find entities connected by specific relationship types.
        
        Args:
            source_id: ID of the source entity
            edge_type: Type of relationship to search for
            
        Returns:
            List of target entity IDs connected to source by the specified edge type
        """
        return [
            target_id for (src_id, target_id), edge in self.edges.items()
            if src_id == source_id and edge.edge_type == edge_type
        ]


class Entity(BaseModel):
    """Core entity with essential fields only"""

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


# Global default entity tree for convenience functions
_default_tree: Optional[EntityTree] = None


def get_default_tree() -> EntityTree:
    """Get or create the default entity tree."""
    global _default_tree
    if _default_tree is None:
        # Create a default entity as root
        root_entity = Entity()
        _default_tree = EntityTree(
            root_ecs_id=root_entity.ecs_id,
            lineage_id=root_entity.lineage_id
        )
        _default_tree.nodes[root_entity.ecs_id] = root_entity
    return _default_tree


def set_default_tree(tree: EntityTree) -> None:
    """Set a custom default entity tree."""
    global _default_tree
    _default_tree = tree


def find_entities_with_component(component_name: str, tree: Optional[EntityTree] = None) -> List[UUID]:
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


def find_entities_by_relationship(source_id: UUID, edge_type: EdgeType, tree: Optional[EntityTree] = None) -> List[UUID]:
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
