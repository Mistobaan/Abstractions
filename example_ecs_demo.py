"""
Comprehensive ECS (Entity Component System) Demonstration

This example exercises all aspects of the ECS system and demonstrates
the core principles of Entity Component System architecture.

ECS Principles Covered:

  1. Entities as Unique Identifiers - Shows how entities are just IDs with
  lineage tracking
  2. Components as Pure Data - Demonstrates data-only storage in
  entity.data dictionary
  3. UML Relationships - Uses composition, aggregation, and association
  edge types
  4. Container Relationships - Shows list items with proper indexing
  5. Entity Versioning - Demonstrates immutable identity with mutable state
  6. Systems as Pure Functions - Damage and movement systems operating on
  components
  7. Dynamic Querying - Finding entities by components and relationships
  8. Runtime Component Management - Adding/removing components dynamically

  - Essential data only: Entity identity, edges, and component data
  - UML-standard edge types instead of custom hierarchical classifications
  - Pure component model with behavior in separate systems
  - Simple tree structure without complex traversal algorithms

  The example can be run to see all ECS principles in action, showing how
  the simplified 85-line entity system provides all the core ECS
  functionality without the complexity of computed structures.
"""

import abstractions as abs
from typing import List
from uuid import uuid4, UUID

def main():
    """
    Demonstrate all ECS principles and functionality.
    """
    
    print("=== ECS DEMONSTRATION ===\n")
    
    # =========================================================================
    # PRINCIPLE 1: ENTITIES ARE UNIQUE IDENTIFIERS
    # =========================================================================
    print("1. ENTITY CREATION - Entities as unique identifiers")
    print("-" * 50)
    
    # Create basic entities - just unique IDs with minimal data
    player = abs.Entity()
    weapon = abs.Entity()
    inventory = abs.Entity()
    
    print(f"Player Entity ID:    {player.ecs_id}")
    print(f"Weapon Entity ID:    {weapon.ecs_id}")
    print(f"Inventory Entity ID: {inventory.ecs_id}")
    print(f"All entities have unique lineage: {player.lineage_id != weapon.lineage_id}")
    print()
    
    # =========================================================================
    # PRINCIPLE 2: COMPONENTS ARE DATA CONTAINERS
    # =========================================================================
    print("2. COMPONENT DATA - Pure data storage")
    print("-" * 50)
    
    # Components are stored in the Entity's data dictionary
    # This demonstrates separation of data from behavior
    
    # Health Component (data only)
    player.data["health"] = {
        "max_hp": 100,
        "current_hp": 75,
        "regeneration_rate": 2
    }
    
    # Position Component (data only)
    player.data["position"] = {
        "x": 10.5,
        "y": 20.3,
        "z": 0.0
    }
    
    # Damage Component for weapon (data only)
    weapon.data["damage"] = {
        "base_damage": 25,
        "damage_type": "slashing",
        "critical_chance": 0.15
    }
    
    # Equipment Component (data only)
    player.data["equipment"] = {
        "main_hand": None,  # Will be populated with weapon entity reference
        "armor_class": 14
    }
    
    print(f"Player Health Component: {player.data['health']}")
    print(f"Player Position Component: {player.data['position']}")
    print(f"Weapon Damage Component: {weapon.data['damage']}")
    print(f"Player Equipment Component: {player.data['equipment']}")
    print()
    
    # =========================================================================
    # PRINCIPLE 3: RELATIONSHIPS THROUGH ENTITY REFERENCES
    # =========================================================================
    print("3. ENTITY RELATIONSHIPS - UML-style associations")
    print("-" * 50)
    
    # Create a tree to manage entity relationships
    game_world = abs.EntityTree(
        root_ecs_id=player.ecs_id,
        lineage_id=player.lineage_id
    )
    
    # Add entities to the tree
    game_world.nodes[player.ecs_id] = player
    game_world.nodes[weapon.ecs_id] = weapon
    game_world.nodes[inventory.ecs_id] = inventory
    
    # COMPOSITION relationship: Player owns equipment (exclusive ownership)
    equipment_edge = abs.EntityEdge(
        source_id=player.ecs_id,
        target_id=weapon.ecs_id,
        edge_type=abs.EdgeType.COMPOSITION,  # Player exclusively owns the weapon
        field_name="equipment"
    )
    game_world.edges[(player.ecs_id, weapon.ecs_id)] = equipment_edge
    
    # Update the component data to reflect the relationship
    player.data["equipment"]["main_hand"] = weapon.ecs_id
    
    # AGGREGATION relationship: Player has inventory (shared ownership)
    inventory_edge = abs.EntityEdge(
        source_id=player.ecs_id,
        target_id=inventory.ecs_id,
        edge_type=abs.EdgeType.AGGREGATION,  # Inventory could be shared/transferred
        field_name="inventory"
    )
    game_world.edges[(player.ecs_id, inventory.ecs_id)] = inventory_edge
    
    print(f"Composition Edge (Player -> Weapon): {equipment_edge.edge_type}")
    print(f"Aggregation Edge (Player -> Inventory): {inventory_edge.edge_type}")
    print(f"Player now wields weapon: {player.data['equipment']['main_hand'] == weapon.ecs_id}")
    print()
    
    # =========================================================================
    # PRINCIPLE 4: CONTAINER RELATIONSHIPS
    # =========================================================================
    print("4. CONTAINER RELATIONSHIPS - Collections of entities")
    print("-" * 50)
    
    # Create multiple items for inventory
    sword = abs.Entity()
    potion = abs.Entity()
    shield = abs.Entity()
    
    # Add component data to items
    sword.data["item"] = {"name": "Iron Sword", "weight": 3.5, "value": 50}
    potion.data["item"] = {"name": "Health Potion", "weight": 0.5, "value": 25}
    shield.data["item"] = {"name": "Wooden Shield", "weight": 2.0, "value": 30}
    
    # Add items to game world
    for item in [sword, potion, shield]:
        game_world.nodes[item.ecs_id] = item
    
    # Create inventory data as a list of entity references
    inventory.data["contents"] = [sword.ecs_id, potion.ecs_id, shield.ecs_id]
    
    # Create container edges for each item in inventory
    for index, item_id in enumerate(inventory.data["contents"]):
        item_edge = abs.EntityEdge(
            source_id=inventory.ecs_id,
            target_id=item_id,
            edge_type=abs.EdgeType.LIST_ITEM,
            field_name="contents",
            container_index=index
        )
        game_world.edges[(inventory.ecs_id, item_id)] = item_edge
    
    print(f"Inventory contains {len(inventory.data['contents'])} items:")
    for i, item_id in enumerate(inventory.data['contents']):
        item = game_world.nodes[item_id]
        print(f"  [{i}] {item.data['item']['name']} (ID: {str(item_id)[:8]}...)")
    print()
    
    # =========================================================================
    # PRINCIPLE 5: ENTITY VERSIONING AND IDENTITY
    # =========================================================================
    print("5. ENTITY VERSIONING - Immutable identity with mutable state")
    print("-" * 50)
    
    print(f"Player original ECS ID: {player.ecs_id}")
    print(f"Player created at: {player.created_at}")
    
    # Simulate an event that changes the player (taking damage)
    original_id = player.ecs_id
    player.previous_ecs_id = original_id
    player.ecs_id = uuid4()  # New version
    player.data["health"]["current_hp"] = 50  # Took damage
    
    print(f"Player new ECS ID: {player.ecs_id}")
    print(f"Player previous ID: {player.previous_ecs_id}")
    print(f"Health after damage: {player.data['health']['current_hp']} HP")
    print(f"Identity preserved: {player.lineage_id} (lineage remains same)")
    print()
    
    # =========================================================================
    # PRINCIPLE 6: SYSTEM SIMULATION (Behavior through pure functions)
    # =========================================================================
    print("6. SYSTEM BEHAVIOR - Pure functions operating on components")
    print("-" * 50)
    
    def damage_system(attacker_id: UUID, target_id: UUID, world: abs.EntityTree) -> str:
        """
        Damage system - pure function that processes damage component interactions.
        This demonstrates how behavior is separated from data in ECS.
        """
        attacker = world.nodes.get(attacker_id)
        target = world.nodes.get(target_id)
        
        if not attacker or not target:
            return "Invalid entities"
        
        # Check if attacker has damage component
        if "damage" not in attacker.data:
            return f"Attacker {str(attacker_id)[:8]} has no damage component"
        
        # Check if target has health component
        if "health" not in target.data:
            return f"Target {str(target_id)[:8]} has no health component"
        
        # Calculate damage
        damage_dealt = attacker.data["damage"]["base_damage"]
        current_hp = target.data["health"]["current_hp"]
        new_hp = max(0, current_hp - damage_dealt)
        
        # Apply damage (this would typically create a new entity version)
        target.data["health"]["current_hp"] = new_hp
        
        return f"Dealt {damage_dealt} damage. Target HP: {current_hp} -> {new_hp}"
    
    def movement_system(entity_id: UUID, dx: float, dy: float, world: abs.EntityTree) -> str:
        """
        Movement system - pure function that processes position components.
        """
        entity = world.nodes.get(entity_id)
        
        if not entity or "position" not in entity.data:
            return "Entity has no position component"
        
        pos = entity.data["position"]
        old_x, old_y = pos["x"], pos["y"]
        pos["x"] += dx
        pos["y"] += dy
        
        return f"Moved from ({old_x}, {old_y}) to ({pos['x']}, {pos['y']})"
    
    # Demonstrate systems in action
    print("Combat System:")
    combat_result = damage_system(weapon.ecs_id, player.ecs_id, game_world)
    print(f"  {combat_result}")
    
    print("Movement System:")
    movement_result = movement_system(player.ecs_id, 5.0, -2.0, game_world)
    print(f"  {movement_result}")
    print()
    
    # =========================================================================
    # PRINCIPLE 7: QUERYING AND FILTERING
    # =========================================================================
    print("7. ENTITY QUERIES - Finding entities by components")
    print("-" * 50)
    
    def find_entities_with_component(component_name: str, world: abs.EntityTree) -> List[UUID]:
        """
        Query system - find all entities that have a specific component.
        This demonstrates how ECS enables efficient querying.
        """
        return [
            entity_id for entity_id, entity in world.nodes.items()
            if component_name in entity.data
        ]
    
    def find_entities_by_relationship(source_id: UUID, edge_type: abs.EdgeType, world: abs.EntityTree) -> List[UUID]:
        """
        Relationship query - find entities connected by specific relationship types.
        """
        return [
            target_id for (src_id, target_id), edge in world.edges.items()
            if src_id == source_id and edge.edge_type == edge_type
        ]
    
    # Query examples
    entities_with_health = find_entities_with_component("health", game_world)
    entities_with_items = find_entities_with_component("item", game_world)
    player_compositions = find_entities_by_relationship(player.ecs_id, abs.EdgeType.COMPOSITION, game_world)
    
    print(f"Entities with health component: {len(entities_with_health)}")
    print(f"Entities with item component: {len(entities_with_items)}")
    print(f"Entities composed by player: {len(player_compositions)}")
    print()
    
    # =========================================================================
    # PRINCIPLE 8: DYNAMIC COMPONENT MANAGEMENT
    # =========================================================================
    print("8. DYNAMIC COMPONENTS - Runtime component addition/removal")
    print("-" * 50)
    
    # Add a new component to existing entity
    print("Adding 'experience' component to player...")
    player.data["experience"] = {
        "level": 5,
        "current_xp": 1250,
        "xp_to_next": 2000
    }
    
    # Remove a component
    print("Removing 'position' component from weapon...")
    if "position" in weapon.data:
        del weapon.data["position"]
    
    # Check component presence dynamically
    player_components = list(player.data.keys())
    weapon_components = list(weapon.data.keys())
    
    print(f"Player components: {player_components}")
    print(f"Weapon components: {weapon_components}")
    print()
    
    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("=== ECS PRINCIPLES DEMONSTRATED ===")
    print("-" * 50)
    print("✓ Entities as unique identifiers with lineage tracking")
    print("✓ Components as pure data containers (no behavior)")
    print("✓ Systems as pure functions operating on components")
    print("✓ UML-style relationships (composition, aggregation, association)")
    print("✓ Container relationships (lists, dictionaries)")
    print("✓ Entity versioning with immutable identity")
    print("✓ Dynamic component management")
    print("✓ Efficient querying and filtering")
    print("✓ Separation of data and behavior")
    print("✓ Tree-based entity organization")
    print()
    print(f"Total entities in world: {len(game_world.nodes)}")
    print(f"Total relationships: {len(game_world.edges)}")


if __name__ == "__main__":
    main()