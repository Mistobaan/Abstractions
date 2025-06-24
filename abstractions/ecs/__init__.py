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
    TreeObserver,
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
    "TreeObserver",
    "find_entities_with_component",
    "find_entities_by_relationship",
    "get_default_tree",
    "set_default_tree",
]
