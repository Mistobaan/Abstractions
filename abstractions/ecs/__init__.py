"""
ECS (Entity Component System) module.
"""

from .entity import (
    ContainerEntity,
    EdgeType,
    Entity,
    EntityEdge,
    EntityTree,
    SimpleEntity,
    find_entities_by_relationship,
    find_entities_with_component,
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
