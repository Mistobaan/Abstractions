"""
Tree change analyzer for detecting differences between EntityTree states.
"""

from typing import Dict, List, Any
from uuid import UUID

from .types import ChangeType, TreeChange
from ..ecs.entity import EntityTree, EntityEdge


class TreeChangeAnalyzer:
    """Analyzes changes between two EntityTree states."""
    
    def __init__(self, old_tree: EntityTree, new_tree: EntityTree):
        self.old_tree = old_tree
        self.new_tree = new_tree
        self.changes: List[TreeChange] = []
    
    def analyze_changes(self) -> List[TreeChange]:
        """
        Perform complete analysis of changes between trees.
        
        Returns:
            List of all changes detected between the trees
        """
        self.changes = []
        
        # Analyze node changes
        self._analyze_node_changes()
        
        # Analyze edge changes
        self._analyze_edge_changes()
        
        # Analyze component changes for existing nodes
        self._analyze_component_changes()
        
        return self.changes
    
    def _analyze_node_changes(self):
        """Analyze additions and removals of nodes."""
        old_nodes = set(self.old_tree.nodes.keys())
        new_nodes = set(self.new_tree.nodes.keys())
        
        # Added nodes
        added_nodes = new_nodes - old_nodes
        for node_id in added_nodes:
            entity = self.new_tree.nodes[node_id]
            self.changes.append(TreeChange(
                change_type=ChangeType.NODE_ADDED,
                entity_id=node_id,
                new_value=entity,
                details={
                    "entity_type": type(entity).__name__,
                    "components": list(entity.data.keys())
                }
            ))
        
        # Removed nodes
        removed_nodes = old_nodes - new_nodes
        for node_id in removed_nodes:
            entity = self.old_tree.nodes[node_id]
            self.changes.append(TreeChange(
                change_type=ChangeType.NODE_REMOVED,
                entity_id=node_id,
                old_value=entity,
                details={
                    "entity_type": type(entity).__name__,
                    "components": list(entity.data.keys())
                }
            ))
    
    def _analyze_edge_changes(self):
        """Analyze additions, removals, and modifications of edges."""
        old_edges = set(self.old_tree.edges.keys())
        new_edges = set(self.new_tree.edges.keys())
        
        # Added edges
        added_edges = new_edges - old_edges
        for edge_key in added_edges:
            edge = self.new_tree.edges[edge_key]
            self.changes.append(TreeChange(
                change_type=ChangeType.EDGE_ADDED,
                edge_key=edge_key,
                new_value=edge,
                details={
                    "source_id": edge.source_id,
                    "target_id": edge.target_id,
                    "edge_type": edge.edge_type,
                    "field_name": edge.field_name
                }
            ))
        
        # Removed edges
        removed_edges = old_edges - new_edges
        for edge_key in removed_edges:
            edge = self.old_tree.edges[edge_key]
            self.changes.append(TreeChange(
                change_type=ChangeType.EDGE_REMOVED,
                edge_key=edge_key,
                old_value=edge,
                details={
                    "source_id": edge.source_id,
                    "target_id": edge.target_id,
                    "edge_type": edge.edge_type,
                    "field_name": edge.field_name
                }
            ))
        
        # Modified edges (same key, different properties)
        common_edges = old_edges & new_edges
        for edge_key in common_edges:
            old_edge = self.old_tree.edges[edge_key]
            new_edge = self.new_tree.edges[edge_key]
            
            if self._edges_differ(old_edge, new_edge):
                self.changes.append(TreeChange(
                    change_type=ChangeType.EDGE_MODIFIED,
                    edge_key=edge_key,
                    old_value=old_edge,
                    new_value=new_edge,
                    details=self._get_edge_differences(old_edge, new_edge)
                ))
    
    def _analyze_component_changes(self):
        """Analyze component changes for entities that exist in both trees."""
        common_nodes = set(self.old_tree.nodes.keys()) & set(self.new_tree.nodes.keys())
        
        for node_id in common_nodes:
            old_entity = self.old_tree.nodes[node_id]
            new_entity = self.new_tree.nodes[node_id]
            
            old_components = set(old_entity.data.keys())
            new_components = set(new_entity.data.keys())
            
            # Added components
            added_components = new_components - old_components
            for component_name in added_components:
                self.changes.append(TreeChange(
                    change_type=ChangeType.COMPONENT_ADDED,
                    entity_id=node_id,
                    component_name=component_name,
                    new_value=new_entity.data[component_name],
                    details={"value_type": type(new_entity.data[component_name]).__name__}
                ))
            
            # Removed components
            removed_components = old_components - new_components
            for component_name in removed_components:
                self.changes.append(TreeChange(
                    change_type=ChangeType.COMPONENT_REMOVED,
                    entity_id=node_id,
                    component_name=component_name,
                    old_value=old_entity.data[component_name],
                    details={"value_type": type(old_entity.data[component_name]).__name__}
                ))
            
            # Modified components
            common_components = old_components & new_components
            for component_name in common_components:
                old_value = old_entity.data[component_name]
                new_value = new_entity.data[component_name]
                
                if old_value != new_value:
                    self.changes.append(TreeChange(
                        change_type=ChangeType.COMPONENT_MODIFIED,
                        entity_id=node_id,
                        component_name=component_name,
                        old_value=old_value,
                        new_value=new_value,
                        details={
                            "old_type": type(old_value).__name__,
                            "new_type": type(new_value).__name__
                        }
                    ))
    
    def _edges_differ(self, edge1: EntityEdge, edge2: EntityEdge) -> bool:
        """Check if two edges have different properties."""
        return (
            edge1.edge_type != edge2.edge_type or
            edge1.field_name != edge2.field_name or
            edge1.container_index != edge2.container_index or
            edge1.container_key != edge2.container_key
        )
    
    def _get_edge_differences(self, old_edge: EntityEdge, new_edge: EntityEdge) -> Dict[str, Any]:
        """Get detailed differences between two edges."""
        differences = {}
        
        if old_edge.edge_type != new_edge.edge_type:
            differences["edge_type"] = {"old": old_edge.edge_type, "new": new_edge.edge_type}
        
        if old_edge.field_name != new_edge.field_name:
            differences["field_name"] = {"old": old_edge.field_name, "new": new_edge.field_name}
        
        if old_edge.container_index != new_edge.container_index:
            differences["container_index"] = {"old": old_edge.container_index, "new": new_edge.container_index}
        
        if old_edge.container_key != new_edge.container_key:
            differences["container_key"] = {"old": old_edge.container_key, "new": new_edge.container_key}
        
        return differences