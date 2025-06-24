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
    TreeObserver,
    find_entities_by_relationship,
    find_entities_with_component,
    get_default_tree,
    set_default_tree,
)

# Import change tracking components
from .change_tracking import (
    ChangeType,
    TreeChange,
    TreeChangeAnalyzer,
    ChangeVisualizer,
    TreeChangeObserver,
    TreeHistoryManager,
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
    "ChangeType",
    "TreeChange",
    "TreeChangeAnalyzer",
    "ChangeVisualizer",
    "TreeChangeObserver",
    "TreeHistoryManager",
]
