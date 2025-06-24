"""
Example: Producing a Full Graph of Changes to an EntityTree

This demonstrates:
1. Observer pattern for real-time change tracking
2. Git-like history management with commits and branches  
3. Efficient analysis between different tree states
4. Visual diff generation with Mermaid diagrams

The change tracking classes have been moved to abstractions.change_tracking module.
"""

from uuid import UUID

import abstractions as abs


def demonstrate_observer_pattern():
    """Demonstrate the observer pattern with real-time change tracking."""
    
    print("=== OBSERVER PATTERN DEMONSTRATION ===\n")
    
    # =========================================================================
    # STEP 1: Set up Observer and Tree
    # =========================================================================
    print("1. SETTING UP OBSERVER PATTERN")
    print("-" * 50)
    
    # Create change observer with git-like history
    observer = abs.TreeChangeObserver(auto_commit=False)
    
    # Create initial entities
    player = abs.Entity()
    weapon = abs.Entity()
    
    # Create tree
    game_world = abs.EntityTree(
        root_ecs_id=player.ecs_id,
        lineage_id=player.lineage_id
    )
    
    # Register observer
    game_world.add_observer(observer)
    observer.register_tree(game_world)
    
    # Set up entity tree references for component notifications
    player.set_tree_reference(game_world)
    weapon.set_tree_reference(game_world)
    
    print(f"Created observer and tree with root: {str(player.ecs_id)[:8]}...")
    print(f"Initial commit created in history")
    print()
    
    # =========================================================================
    # STEP 2: Demonstrate Real-time Change Tracking
    # =========================================================================
    print("2. REAL-TIME CHANGE TRACKING")
    print("-" * 50)
    
    # Add nodes (triggers observer notifications)
    print("Adding entities to tree...")
    game_world.add_node(player)
    game_world.add_node(weapon)
    
    # Add components (triggers observer notifications)
    print("Adding components...")
    player.add_component("health", {"hp": 100, "max_hp": 100})
    player.add_component("position", {"x": 0, "y": 0})
    weapon.add_component("damage", {"value": 20, "type": "sword"})
    
    # Add edges (triggers observer notifications)
    print("Adding relationships...")
    equipment_edge = abs.EntityEdge(
        source_id=player.ecs_id,
        target_id=weapon.ecs_id,
        edge_type=abs.EdgeType.COMPOSITION,
        field_name="equipment"
    )
    game_world.add_edge(equipment_edge)
    
    # Commit current state
    commit1 = observer.commit_current_state(player.ecs_id, "Initial game state")
    print(f"Committed changes: {commit1[:8]}...")
    print()
    
    # =========================================================================
    # STEP 3: Make More Changes
    # =========================================================================
    print("3. MAKING ADDITIONAL CHANGES")
    print("-" * 50)
    
    # Modify components
    print("Modifying components...")
    player.update_component("health", {"hp": 75, "max_hp": 100})  # Player took damage
    weapon.update_component("damage", {"value": 25, "type": "sword"})  # Weapon upgraded
    
    # Add new entity
    print("Adding new entity...")
    armor = abs.Entity()
    armor.set_tree_reference(game_world)
    game_world.add_node(armor)
    armor.add_component("defense", {"value": 15, "type": "leather"})
    
    # Add new edge
    armor_edge = abs.EntityEdge(
        source_id=player.ecs_id,
        target_id=armor.ecs_id,
        edge_type=abs.EdgeType.COMPOSITION,
        field_name="armor"
    )
    game_world.add_edge(armor_edge)
    
    # Remove a component
    print("Removing component...")
    weapon.remove_component("damage")
    
    # Commit changes
    commit2 = observer.commit_current_state(player.ecs_id, "Player progression and equipment")
    print(f"Committed changes: {commit2[:8]}...")
    print()
    
    # =========================================================================
    # STEP 4: Analyze History
    # =========================================================================
    print("4. ANALYZING CHANGE HISTORY")
    print("-" * 50)
    
    # Get commit history
    history = observer.get_history_for_tree(player.ecs_id)
    print(f"Total commits in history: {len(history)}")
    
    for i, snapshot in enumerate(history):
        print(f"  Commit {i+1}: {snapshot.commit_id[:8]}... - {snapshot.message}")
        print(f"    Timestamp: {snapshot.timestamp}")
        print(f"    Events: {len(snapshot.events)}")
    
    print()
    
    # =========================================================================
    # STEP 5: Analyze Evolution
    # =========================================================================
    print("5. ANALYZING TREE EVOLUTION")
    print("-" * 50)
    
    # Analyze changes between commits
    evolution = observer.analyze_evolution(player.ecs_id, commit1, commit2)
    print(f"Changes between commits: {len(evolution)}")
    
    # Create visualizer
    visualizer = abs.ChangeVisualizer(evolution)
    summary = visualizer.generate_summary()
    print(summary)
    
    return observer, game_world


def demonstrate_git_like_features():
    """Demonstrate git-like features: branches, merges, and analysis."""
    
    print("=== GIT-LIKE FEATURES DEMONSTRATION ===\n")
    
    # =========================================================================
    # STEP 1: Create History Manager and Branches
    # =========================================================================
    print("1. BRANCH MANAGEMENT")
    print("-" * 50)
    
    observer = abs.TreeChangeObserver()
    
    # Create base tree
    player = abs.Entity()
    base_tree = abs.EntityTree(
        root_ecs_id=player.ecs_id,
        lineage_id=player.lineage_id
    )
    base_tree.add_observer(observer)
    observer.register_tree(base_tree)
    
    player.set_tree_reference(base_tree)
    base_tree.add_node(player)
    player.add_component("health", {"hp": 100})
    player.add_component("level", {"value": 1})
    
    # Create initial commit
    main_commit = observer.commit_current_state(player.ecs_id, "Initial player", "main")
    print(f"Main branch created: {main_commit[:8]}...")
    
    # Create development branch
    dev_branch = observer.create_branch_from_current(player.ecs_id, "development")
    print(f"Development branch created: {dev_branch}")
    
    # Make changes on development branch
    player.update_component("level", {"value": 5})
    player.add_component("experience", {"xp": 1250})
    dev_commit = observer.commit_current_state(player.ecs_id, "Level up system", "development")
    print(f"Development commit: {dev_commit[:8]}...")
    
    # List branches
    branches = observer.history_manager.list_branches()
    print(f"Available branches: {branches}")
    print()
    
    # =========================================================================
    # STEP 2: Analyze Different Branches
    # =========================================================================
    print("2. CROSS-BRANCH ANALYSIS")
    print("-" * 50)
    
    # Compare main and development branches
    main_head = observer.history_manager.get_branch_head("main")
    dev_head = observer.history_manager.get_branch_head("development")
    
    branch_diff = observer.history_manager.analyze_changes_between_commits(main_head, dev_head)
    print(f"Changes from main to development: {len(branch_diff)}")
    
    diff_visualizer = abs.ChangeVisualizer(branch_diff)
    print(diff_visualizer.generate_summary())
    
    # Find common ancestor
    common = observer.history_manager.get_common_ancestor(main_head, dev_head)
    print(f"Common ancestor: {common[:8] if common else 'None'}...")
    print()
    
    return observer


def demonstrate_tree_changes():
    """Original comprehensive demonstration updated to use new module structure."""
    
    print("=== COMPREHENSIVE CHANGE TRACKING ===\n")
    
    # Create observer for tracking
    observer = abs.TreeChangeObserver()
    
    # Create and track original tree
    player = abs.Entity()
    weapon = abs.Entity()
    inventory = abs.Entity()
    
    original_tree = abs.EntityTree(
        root_ecs_id=player.ecs_id,
        lineage_id=player.lineage_id
    )
    
    # Set up observer
    original_tree.add_observer(observer)
    observer.register_tree(original_tree)
    
    # Set up entities
    player.set_tree_reference(original_tree)
    weapon.set_tree_reference(original_tree)
    inventory.set_tree_reference(original_tree)
    
    # Build initial state
    original_tree.add_node(player)
    original_tree.add_node(weapon)
    original_tree.add_node(inventory)
    
    player.add_component("health", {"hp": 100, "max_hp": 100})
    player.add_component("position", {"x": 0, "y": 0})
    weapon.add_component("damage", {"value": 20, "type": "sword"})
    inventory.add_component("storage", {"capacity": 50})
    
    # Add relationships
    equipment_edge = abs.EntityEdge(
        source_id=player.ecs_id,
        target_id=weapon.ecs_id,
        edge_type=abs.EdgeType.COMPOSITION,
        field_name="equipment"
    )
    original_tree.add_edge(equipment_edge)
    
    inventory_edge = abs.EntityEdge(
        source_id=player.ecs_id,
        target_id=inventory.ecs_id,
        edge_type=abs.EdgeType.AGGREGATION,
        field_name="inventory"
    )
    original_tree.add_edge(inventory_edge)
    
    # Commit initial state
    commit1 = observer.commit_current_state(player.ecs_id, "Initial state")
    print(f"Initial tree committed: {commit1[:8]}...")
    
    # Make comprehensive changes
    player.update_component("health", {"hp": 75, "max_hp": 100})
    player.update_component("position", {"x": 10, "y": 5})
    weapon.update_component("damage", {"value": 25, "type": "sword"})
    
    player.add_component("experience", {"level": 5, "xp": 1250})
    weapon.add_component("enchantment", {"type": "fire", "damage_bonus": 5})
    
    inventory.remove_component("storage")
    
    # Add new entity
    armor = abs.Entity()
    armor.set_tree_reference(original_tree)
    original_tree.add_node(armor)
    armor.add_component("defense", {"value": 15, "type": "leather"})
    
    # Add new edge
    armor_edge = abs.EntityEdge(
        source_id=player.ecs_id,
        target_id=armor.ecs_id,
        edge_type=abs.EdgeType.COMPOSITION,
        field_name="armor"
    )
    original_tree.add_edge(armor_edge)
    
    # Remove weapon
    original_tree.remove_node(weapon.ecs_id)
    original_tree.remove_edge(player.ecs_id, weapon.ecs_id)
    
    # Commit modified state
    commit2 = observer.commit_current_state(player.ecs_id, "Major changes")
    print(f"Modified tree committed: {commit2[:8]}...")
    
    # Analyze comprehensive changes
    all_changes = observer.analyze_evolution(player.ecs_id, commit1, commit2)
    print(f"Total changes detected: {len(all_changes)}")
    
    # Generate reports
    visualizer = abs.ChangeVisualizer(all_changes)
    detailed_report = visualizer.generate_detailed_report()
    print("\nDETAILED CHANGE REPORT:")
    print("=" * 50)
    print(detailed_report)
    
    # Generate visual diff
    tree1 = observer.history_manager.get_tree_at_commit(commit1)
    tree2 = observer.history_manager.get_tree_at_commit(commit2)
    
    if tree1 and tree2:
        mermaid_diff = visualizer.generate_mermaid_diff(tree1, tree2)
        print("\nVISUAL DIFF DIAGRAM:")
        print("-" * 50)
        print(mermaid_diff)
    
    return observer


def main():
    """Run all demonstrations."""
    
    print("🎯 ENTITY TREE CHANGE TRACKING WITH OBSERVER PATTERN")
    print("=" * 60)
    print()
    
    # Demonstrate observer pattern
    observer1, tree1 = demonstrate_observer_pattern()
    
    print("\n" + "=" * 60 + "\n")
    
    # Demonstrate git-like features
    observer2 = demonstrate_git_like_features()
    
    print("\n" + "=" * 60 + "\n")
    
    # Demonstrate comprehensive analysis
    observer3 = demonstrate_tree_changes()
    
    print("\n" + "=" * 60)
    print("🎉 ALL DEMONSTRATIONS COMPLETE")
    print("=" * 60)
    print()
    print("Key Features Demonstrated:")
    print("✓ Real-time change tracking with observer pattern")
    print("✓ Git-like commit and branch management")  
    print("✓ Efficient cross-commit analysis")
    print("✓ Visual diff generation with Mermaid")
    print("✓ Component, node, and edge change detection")
    print("✓ Automatic event capture and history building")



if __name__ == "__main__":
    main()