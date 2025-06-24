"""
Abstractions package - Entity Component System and related abstractions.
"""

# Import core ECS classes to top level for easy access
from .ecs import (
    ContainerEntity,
    EdgeType,
    Entity,
    EntityEdge,
    EntityTree,
    SimpleEntity,
    find_entities_with_component,
    find_entities_by_relationship,
    get_default_tree,
    set_default_tree,
)

__all__ = [
    "EdgeType",
    "Entity",
    "EntityEdge",
    "EntityTree",
    "SimpleEntity",
    "ContainerEntity",
    "find_entities_with_component",
    "find_entities_by_relationship",
    "get_default_tree",
    "set_default_tree",
]
