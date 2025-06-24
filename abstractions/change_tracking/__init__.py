"""
Change tracking module for EntityTree diff analysis and git-like history.
"""

from .types import ChangeType, TreeChange
from .analyzer import TreeChangeAnalyzer
from .visualizer import ChangeVisualizer
from .observer import TreeChangeObserver, TreeHistoryManager
from .events import (
    TreeEvent,
    NodeAddedEvent,
    NodeRemovedEvent,
    NodeModifiedEvent,
    EdgeAddedEvent,
    EdgeRemovedEvent,
    EdgeModifiedEvent,
    ComponentAddedEvent,
    ComponentRemovedEvent,
    ComponentModifiedEvent,
)

__all__ = [
    "ChangeType",
    "TreeChange",
    "TreeChangeAnalyzer", 
    "ChangeVisualizer",
    "TreeChangeObserver",
    "TreeHistoryManager",
    "TreeEvent",
    "NodeAddedEvent",
    "NodeRemovedEvent", 
    "NodeModifiedEvent",
    "EdgeAddedEvent",
    "EdgeRemovedEvent",
    "EdgeModifiedEvent",
    "ComponentAddedEvent",
    "ComponentRemovedEvent",
    "ComponentModifiedEvent",
]