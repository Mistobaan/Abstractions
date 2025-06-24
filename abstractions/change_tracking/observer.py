"""
Observer pattern implementation for EntityTree change tracking with git-like history.
"""

from abc import ABC, abstractmethod
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from typing import Dict, List, Optional, Protocol, Set
from uuid import UUID, uuid4

from .events import TreeEvent
from .types import TreeChange
from ..ecs.entity import EntityTree


class TreeObserver(Protocol):
    """Protocol for tree observers."""
    
    def notify(self, event: TreeEvent) -> None:
        """Handle a tree event."""
        ...


class Observable:
    """Base class for observable objects."""
    
    def __init__(self):
        self._observers: List[TreeObserver] = []
    
    def add_observer(self, observer: TreeObserver) -> None:
        """Add an observer."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer: TreeObserver) -> None:
        """Remove an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_observers(self, event: TreeEvent) -> None:
        """Notify all observers of an event."""
        for observer in self._observers:
            observer.notify(event)


class TreeSnapshot:
    """Represents a snapshot of a tree at a specific point in time."""
    
    def __init__(self, tree: EntityTree, commit_id: str = None, parent_commits: List[str] = None):
        self.tree = deepcopy(tree)
        self.commit_id = commit_id or str(uuid4())
        self.parent_commits = parent_commits or []
        self.timestamp = datetime.now(timezone.utc)
        self.events: List[TreeEvent] = []
        self.message = ""
    
    def add_event(self, event: TreeEvent) -> None:
        """Add an event to this snapshot."""
        self.events.append(event)


class TreeHistoryManager:
    """
    Manages git-like history for EntityTrees with efficient analysis capabilities.
    
    Features:
    - Commit-based snapshots of tree states
    - Branch management for different tree lineages
    - Efficient diff analysis between commits
    - Merge capabilities for concurrent changes
    """
    
    def __init__(self):
        # Commit storage: commit_id -> TreeSnapshot
        self.commits: Dict[str, TreeSnapshot] = {}
        
        # Branch tracking: branch_name -> commit_id
        self.branches: Dict[str, str] = {}
        
        # Root tracking: root_ecs_id -> Set[commit_ids]
        self.root_commits: Dict[UUID, Set[str]] = defaultdict(set)
        
        # Current head for each root
        self.heads: Dict[UUID, str] = {}
        
        # Lineage tracking: lineage_id -> Set[commit_ids]
        self.lineage_commits: Dict[UUID, Set[str]] = defaultdict(set)
    
    def commit_tree(
        self, 
        tree: EntityTree, 
        message: str = "", 
        parent_commits: List[str] = None,
        branch: str = "main"
    ) -> str:
        """
        Commit a tree snapshot to history.
        
        Args:
            tree: The EntityTree to commit
            message: Commit message
            parent_commits: Parent commit IDs (for merges)
            branch: Branch name
            
        Returns:
            The commit ID of the new snapshot
        """
        # Create snapshot
        snapshot = TreeSnapshot(tree, parent_commits=parent_commits)
        snapshot.message = message
        
        # Store commit
        self.commits[snapshot.commit_id] = snapshot
        
        # Update branch
        self.branches[branch] = snapshot.commit_id
        
        # Update root tracking
        self.root_commits[tree.root_ecs_id].add(snapshot.commit_id)
        self.heads[tree.root_ecs_id] = snapshot.commit_id
        
        # Update lineage tracking
        self.lineage_commits[tree.lineage_id].add(snapshot.commit_id)
        
        return snapshot.commit_id
    
    def get_commit(self, commit_id: str) -> Optional[TreeSnapshot]:
        """Get a commit by ID."""
        return self.commits.get(commit_id)
    
    def get_tree_at_commit(self, commit_id: str) -> Optional[EntityTree]:
        """Get the tree state at a specific commit."""
        snapshot = self.get_commit(commit_id)
        return snapshot.tree if snapshot else None
    
    def get_commits_for_root(self, root_ecs_id: UUID) -> List[str]:
        """Get all commits for a specific root entity."""
        return list(self.root_commits.get(root_ecs_id, set()))
    
    def get_commits_for_lineage(self, lineage_id: UUID) -> List[str]:
        """Get all commits for a specific lineage."""
        return list(self.lineage_commits.get(lineage_id, set()))
    
    def get_common_ancestor(self, commit1: str, commit2: str) -> Optional[str]:
        """
        Find the common ancestor of two commits.
        
        This is useful for merge analysis and finding divergence points.
        """
        # Simple implementation - can be optimized with more sophisticated algorithms
        ancestors1 = self._get_ancestors(commit1)
        ancestors2 = self._get_ancestors(commit2)
        
        common = ancestors1 & ancestors2
        if not common:
            return None
        
        # Return the most recent common ancestor
        # For now, just return any common ancestor
        return next(iter(common))
    
    def _get_ancestors(self, commit_id: str) -> Set[str]:
        """Get all ancestor commits of a given commit."""
        ancestors = set()
        to_visit = [commit_id]
        
        while to_visit:
            current = to_visit.pop()
            if current in ancestors:
                continue
                
            ancestors.add(current)
            snapshot = self.get_commit(current)
            if snapshot:
                to_visit.extend(snapshot.parent_commits)
        
        return ancestors
    
    def create_branch(self, branch_name: str, from_commit: str) -> bool:
        """Create a new branch from a specific commit."""
        if branch_name in self.branches:
            return False
        
        if from_commit not in self.commits:
            return False
        
        self.branches[branch_name] = from_commit
        return True
    
    def get_branch_head(self, branch_name: str) -> Optional[str]:
        """Get the head commit of a branch."""
        return self.branches.get(branch_name)
    
    def list_branches(self) -> List[str]:
        """List all branch names."""
        return list(self.branches.keys())
    
    def analyze_changes_between_commits(self, from_commit: str, to_commit: str) -> List[TreeChange]:
        """
        Analyze changes between two commits.
        
        This provides efficient diff analysis for any two tree states.
        """
        from .analyzer import TreeChangeAnalyzer
        
        from_tree = self.get_tree_at_commit(from_commit)
        to_tree = self.get_tree_at_commit(to_commit)
        
        if not from_tree or not to_tree:
            return []
        
        analyzer = TreeChangeAnalyzer(from_tree, to_tree)
        return analyzer.analyze_changes()
    
    def get_commit_log(self, root_ecs_id: UUID = None, limit: int = None) -> List[TreeSnapshot]:
        """
        Get commit log for analysis.
        
        Args:
            root_ecs_id: Filter by specific root entity (optional)
            limit: Maximum number of commits to return
            
        Returns:
            List of snapshots sorted by timestamp (newest first)
        """
        if root_ecs_id:
            commit_ids = self.get_commits_for_root(root_ecs_id)
        else:
            commit_ids = list(self.commits.keys())
        
        snapshots = [self.commits[cid] for cid in commit_ids if cid in self.commits]
        snapshots.sort(key=lambda s: s.timestamp, reverse=True)
        
        if limit:
            snapshots = snapshots[:limit]
        
        return snapshots


class TreeChangeObserver:
    """
    Observer that tracks all changes to EntityTrees and maintains git-like history.
    
    This observer automatically captures changes and can create commits,
    manage branches, and provide efficient analysis of tree evolution.
    """
    
    def __init__(self, auto_commit: bool = False):
        self.history_manager = TreeHistoryManager()
        self.auto_commit = auto_commit
        self.pending_events: Dict[UUID, List[TreeEvent]] = defaultdict(list)
        
        # Track current tree states
        self.current_trees: Dict[UUID, EntityTree] = {}
    
    def notify(self, event: TreeEvent) -> None:
        """Handle a tree event."""
        if event.tree_id:
            self.pending_events[event.tree_id].append(event)
            
            if self.auto_commit:
                self._auto_commit_changes(event.tree_id)
    
    def register_tree(self, tree: EntityTree) -> None:
        """Register a tree for tracking."""
        self.current_trees[tree.root_ecs_id] = tree
        
        # Create initial commit if this is the first time we see this tree
        if not self.history_manager.get_commits_for_root(tree.root_ecs_id):
            self.commit_current_state(tree.root_ecs_id, "Initial commit")
    
    def commit_current_state(
        self, 
        root_ecs_id: UUID, 
        message: str = "Auto-commit",
        branch: str = "main"
    ) -> Optional[str]:
        """
        Commit the current state of a tree.
        
        Args:
            root_ecs_id: Root entity ID to commit
            message: Commit message
            branch: Branch name
            
        Returns:
            Commit ID if successful, None otherwise
        """
        tree = self.current_trees.get(root_ecs_id)
        if not tree:
            return None
        
        # Get parent commit (current head)
        parent_commits = []
        current_head = self.history_manager.heads.get(root_ecs_id)
        if current_head:
            parent_commits = [current_head]
        
        # Create commit
        commit_id = self.history_manager.commit_tree(
            tree, message, parent_commits, branch
        )
        
        # Add pending events to the commit
        snapshot = self.history_manager.get_commit(commit_id)
        if snapshot:
            events = self.pending_events.get(root_ecs_id, [])
            for event in events:
                snapshot.add_event(event)
            
            # Clear pending events
            self.pending_events[root_ecs_id] = []
        
        return commit_id
    
    def _auto_commit_changes(self, tree_id: UUID) -> None:
        """Auto-commit changes when enough events have accumulated."""
        events = self.pending_events.get(tree_id, [])
        
        # Auto-commit after 10 events (configurable)
        if len(events) >= 10:
            self.commit_current_state(tree_id, f"Auto-commit: {len(events)} changes")
    
    def get_history_for_tree(self, root_ecs_id: UUID) -> List[TreeSnapshot]:
        """Get the full history for a specific tree."""
        return self.history_manager.get_commit_log(root_ecs_id)
    
    def analyze_evolution(
        self, 
        root_ecs_id: UUID, 
        from_commit: str = None, 
        to_commit: str = None
    ) -> List[TreeChange]:
        """
        Analyze how a tree has evolved between two points.
        
        Args:
            root_ecs_id: Root entity to analyze
            from_commit: Starting commit (uses first commit if None)
            to_commit: Ending commit (uses latest if None)
            
        Returns:
            List of changes between the commits
        """
        commits = self.history_manager.get_commits_for_root(root_ecs_id)
        if len(commits) < 2:
            return []
        
        if not from_commit:
            # Use earliest commit
            snapshots = self.history_manager.get_commit_log(root_ecs_id)
            from_commit = snapshots[-1].commit_id if snapshots else None
        
        if not to_commit:
            # Use latest commit
            to_commit = self.history_manager.heads.get(root_ecs_id)
        
        if not from_commit or not to_commit:
            return []
        
        return self.history_manager.analyze_changes_between_commits(from_commit, to_commit)
    
    def create_branch_from_current(self, root_ecs_id: UUID, branch_name: str) -> bool:
        """Create a new branch from the current state of a tree."""
        current_head = self.history_manager.heads.get(root_ecs_id)
        if not current_head:
            return False
        
        return self.history_manager.create_branch(branch_name, current_head)