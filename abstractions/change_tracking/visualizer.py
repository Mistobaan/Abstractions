"""
Visualizes tree changes in various formats.
"""

from typing import Any, List

from .types import ChangeType, TreeChange
from ..ecs.entity import Entity, EntityEdge, EntityTree


class ChangeVisualizer:
    """Visualizes tree changes in various formats."""
    
    def __init__(self, changes: List[TreeChange]):
        self.changes = changes
    
    def generate_summary(self) -> str:
        """Generate a summary of all changes."""
        summary = ["=== ENTITY TREE CHANGE SUMMARY ===", ""]
        
        # Count changes by type
        change_counts = {}
        for change in self.changes:
            change_counts[change.change_type] = change_counts.get(change.change_type, 0) + 1
        
        summary.append("Change Type Counts:")
        for change_type, count in sorted(change_counts.items()):
            summary.append(f"  {change_type}: {count}")
        
        summary.append(f"\nTotal Changes: {len(self.changes)}")
        summary.append("")
        
        return "\n".join(summary)
    
    def generate_detailed_report(self) -> str:
        """Generate a detailed report of all changes."""
        report = [self.generate_summary()]
        
        # Group changes by type
        changes_by_type = {}
        for change in self.changes:
            if change.change_type not in changes_by_type:
                changes_by_type[change.change_type] = []
            changes_by_type[change.change_type].append(change)
        
        # Generate detailed sections
        for change_type, type_changes in sorted(changes_by_type.items()):
            report.append(f"=== {change_type.upper()} ===")
            report.append("")
            
            for change in type_changes:
                report.append(self._format_change_detail(change))
                report.append("")
        
        return "\n".join(report)
    
    def _format_change_detail(self, change: TreeChange) -> str:
        """Format a single change for detailed output."""
        lines = []
        
        if change.entity_id:
            lines.append(f"Entity: {str(change.entity_id)[:8]}...")
        
        if change.edge_key:
            src_id, tgt_id = change.edge_key
            lines.append(f"Edge: {str(src_id)[:8]}... -> {str(tgt_id)[:8]}...")
        
        if change.component_name:
            lines.append(f"Component: {change.component_name}")
        
        if change.old_value is not None:
            lines.append(f"Old Value: {self._format_value(change.old_value)}")
        
        if change.new_value is not None:
            lines.append(f"New Value: {self._format_value(change.new_value)}")
        
        if change.details:
            lines.append(f"Details: {change.details}")
        
        return "  " + "\n  ".join(lines)
    
    def _format_value(self, value: Any) -> str:
        """Format a value for display."""
        if isinstance(value, Entity):
            return f"Entity({type(value).__name__})"
        elif isinstance(value, EntityEdge):
            return f"Edge({value.edge_type}, {value.field_name})"
        elif isinstance(value, dict):
            return f"Dict[{len(value)} items]"
        elif isinstance(value, list):
            return f"List[{len(value)} items]"
        else:
            return str(value)
    
    def generate_mermaid_diff(self, old_tree: EntityTree, new_tree: EntityTree) -> str:
        """Generate a Mermaid diagram showing changes between trees."""
        lines = [
            "```mermaid",
            "graph TD",
            "  %% Entity Tree Change Visualization",
            ""
        ]
        
        # Show all nodes with change indicators
        all_nodes = set(old_tree.nodes.keys()) | set(new_tree.nodes.keys())
        
        for node_id in all_nodes:
            short_id = str(node_id)[:8]
            
            if node_id in old_tree.nodes and node_id in new_tree.nodes:
                # Existing node - check if modified
                has_changes = any(
                    change.entity_id == node_id and change.change_type == ChangeType.COMPONENT_MODIFIED
                    for change in self.changes
                )
                style = "modifiedNode" if has_changes else "unchangedNode"
                entity_type = type(new_tree.nodes[node_id]).__name__
            elif node_id in new_tree.nodes:
                # Added node
                style = "addedNode"
                entity_type = type(new_tree.nodes[node_id]).__name__
            else:
                # Removed node
                style = "removedNode"
                entity_type = type(old_tree.nodes[node_id]).__name__
            
            lines.append(f"  {node_id}[\"{entity_type}\\n{short_id}\"]:::{style}")
        
        lines.append("")
        
        # Show edges with change indicators
        all_edges = set(old_tree.edges.keys()) | set(new_tree.edges.keys())
        
        for edge_key in all_edges:
            src_id, tgt_id = edge_key
            
            if edge_key in old_tree.edges and edge_key in new_tree.edges:
                # Existing edge
                edge = new_tree.edges[edge_key]
                lines.append(f"  {src_id} -->|{edge.field_name}| {tgt_id}")
            elif edge_key in new_tree.edges:
                # Added edge
                edge = new_tree.edges[edge_key]
                lines.append(f"  {src_id} -.->|+{edge.field_name}| {tgt_id}")
            else:
                # Removed edge
                edge = old_tree.edges[edge_key]
                lines.append(f"  {src_id} -.->|-{edge.field_name}| {tgt_id}")
        
        # Add styling
        lines.extend([
            "",
            "  classDef addedNode fill:#90EE90,stroke:#228B22,stroke-width:2px",
            "  classDef removedNode fill:#FFB6C1,stroke:#DC143C,stroke-width:2px",
            "  classDef modifiedNode fill:#FFD700,stroke:#FFA500,stroke-width:2px",
            "  classDef unchangedNode fill:#E6E6FA,stroke:#9370DB,stroke-width:1px",
            "```"
        ])
        
        return "\n".join(lines)