"""
Tests for EntityTree query methods and root-level query functions.
"""

import unittest
from uuid import uuid4, UUID

import abstractions as abs


class TestEntityTreeQueryMethods(unittest.TestCase):
    """Test the query methods added to EntityTree class."""

    def setUp(self):
        """Set up test entities and tree for each test."""
        # Create entities
        self.root_entity = abs.Entity()
        self.player = abs.Entity()
        self.weapon = abs.Entity()
        self.inventory = abs.Entity()
        self.potion = abs.Entity()
        
        # Create tree
        self.tree = abs.EntityTree(
            root_ecs_id=self.root_entity.ecs_id,
            lineage_id=self.root_entity.lineage_id
        )
        
        # Add entities to tree
        entities = [self.root_entity, self.player, self.weapon, self.inventory, self.potion]
        for entity in entities:
            self.tree.nodes[entity.ecs_id] = entity
        
        # Add component data
        self.player.data["health"] = {"hp": 100, "max_hp": 100}
        self.player.data["position"] = {"x": 10, "y": 20}
        self.weapon.data["damage"] = {"value": 25, "type": "sword"}
        self.inventory.data["storage"] = {"capacity": 50, "used": 10}
        self.potion.data["health"] = {"heal": 50}  # Also has health component
        self.potion.data["item"] = {"name": "Health Potion"}
        
        # Add relationships
        self.composition_edge = abs.EntityEdge(
            source_id=self.player.ecs_id,
            target_id=self.weapon.ecs_id,
            edge_type=abs.EdgeType.COMPOSITION,
            field_name="equipment"
        )
        self.tree.edges[(self.player.ecs_id, self.weapon.ecs_id)] = self.composition_edge
        
        self.aggregation_edge = abs.EntityEdge(
            source_id=self.player.ecs_id,
            target_id=self.inventory.ecs_id,
            edge_type=abs.EdgeType.AGGREGATION,
            field_name="inventory"
        )
        self.tree.edges[(self.player.ecs_id, self.inventory.ecs_id)] = self.aggregation_edge
        
        self.list_edge = abs.EntityEdge(
            source_id=self.inventory.ecs_id,
            target_id=self.potion.ecs_id,
            edge_type=abs.EdgeType.LIST_ITEM,
            field_name="contents",
            container_index=0
        )
        self.tree.edges[(self.inventory.ecs_id, self.potion.ecs_id)] = self.list_edge

    def test_find_entities_with_component(self):
        """Test finding entities by component name."""
        # Test finding entities with 'health' component
        health_entities = self.tree.find_entities_with_component("health")
        self.assertEqual(len(health_entities), 2)
        self.assertIn(self.player.ecs_id, health_entities)
        self.assertIn(self.potion.ecs_id, health_entities)
        
        # Test finding entities with 'damage' component
        damage_entities = self.tree.find_entities_with_component("damage")
        self.assertEqual(len(damage_entities), 1)
        self.assertIn(self.weapon.ecs_id, damage_entities)
        
        # Test finding entities with 'position' component
        position_entities = self.tree.find_entities_with_component("position")
        self.assertEqual(len(position_entities), 1)
        self.assertIn(self.player.ecs_id, position_entities)
        
        # Test finding entities with non-existent component
        missing_entities = self.tree.find_entities_with_component("nonexistent")
        self.assertEqual(len(missing_entities), 0)

    def test_find_entities_by_relationship(self):
        """Test finding entities by relationship type."""
        # Test finding composition relationships from player
        composition_targets = self.tree.find_entities_by_relationship(
            self.player.ecs_id, abs.EdgeType.COMPOSITION
        )
        self.assertEqual(len(composition_targets), 1)
        self.assertIn(self.weapon.ecs_id, composition_targets)
        
        # Test finding aggregation relationships from player
        aggregation_targets = self.tree.find_entities_by_relationship(
            self.player.ecs_id, abs.EdgeType.AGGREGATION
        )
        self.assertEqual(len(aggregation_targets), 1)
        self.assertIn(self.inventory.ecs_id, aggregation_targets)
        
        # Test finding list item relationships from inventory
        list_targets = self.tree.find_entities_by_relationship(
            self.inventory.ecs_id, abs.EdgeType.LIST_ITEM
        )
        self.assertEqual(len(list_targets), 1)
        self.assertIn(self.potion.ecs_id, list_targets)
        
        # Test finding relationships from entity with no outgoing edges
        no_targets = self.tree.find_entities_by_relationship(
            self.weapon.ecs_id, abs.EdgeType.COMPOSITION
        )
        self.assertEqual(len(no_targets), 0)
        
        # Test finding non-existent relationship type
        association_targets = self.tree.find_entities_by_relationship(
            self.player.ecs_id, abs.EdgeType.ASSOCIATION
        )
        self.assertEqual(len(association_targets), 0)

    def test_query_methods_with_empty_tree(self):
        """Test query methods on empty tree."""
        empty_tree = abs.EntityTree(
            root_ecs_id=uuid4(),
            lineage_id=uuid4()
        )
        
        # Test component search on empty tree
        entities = empty_tree.find_entities_with_component("health")
        self.assertEqual(len(entities), 0)
        
        # Test relationship search on empty tree
        relationships = empty_tree.find_entities_by_relationship(
            uuid4(), abs.EdgeType.COMPOSITION
        )
        self.assertEqual(len(relationships), 0)

    def test_query_methods_return_types(self):
        """Test that query methods return correct types."""
        # Test return type for component search
        result = self.tree.find_entities_with_component("health")
        self.assertIsInstance(result, list)
        for item in result:
            self.assertIsInstance(item, UUID)
        
        # Test return type for relationship search
        result = self.tree.find_entities_by_relationship(
            self.player.ecs_id, abs.EdgeType.COMPOSITION
        )
        self.assertIsInstance(result, list)
        for item in result:
            self.assertIsInstance(item, UUID)


class TestRootLevelQueryFunctions(unittest.TestCase):
    """Test the root-level query functions that use default EntityTree."""

    def setUp(self):
        """Set up test data for each test."""
        # Reset the default tree for each test
        abs.set_default_tree(None)
        
        # Create test entities
        self.entity1 = abs.Entity()
        self.entity2 = abs.Entity()
        self.entity3 = abs.Entity()
        
        # Add component data
        self.entity1.data["health"] = {"hp": 100}
        self.entity1.data["player"] = {"name": "Alice"}
        self.entity2.data["health"] = {"hp": 75}
        self.entity2.data["enemy"] = {"type": "orc"}
        self.entity3.data["item"] = {"name": "sword"}

    def test_default_tree_creation(self):
        """Test that default tree is created automatically."""
        # First call should create the default tree
        tree1 = abs.get_default_tree()
        self.assertIsInstance(tree1, abs.EntityTree)
        
        # Second call should return the same tree
        tree2 = abs.get_default_tree()
        self.assertIs(tree1, tree2)
        
        # Tree should have a root entity
        self.assertEqual(len(tree1.nodes), 1)

    def test_set_custom_default_tree(self):
        """Test setting a custom default tree."""
        # Create custom tree
        custom_root = abs.Entity()
        custom_tree = abs.EntityTree(
            root_ecs_id=custom_root.ecs_id,
            lineage_id=custom_root.lineage_id
        )
        custom_tree.nodes[custom_root.ecs_id] = custom_root
        
        # Set as default
        abs.set_default_tree(custom_tree)
        
        # Verify it's used as default
        retrieved_tree = abs.get_default_tree()
        self.assertIs(retrieved_tree, custom_tree)

    def test_find_entities_with_component_default_tree(self):
        """Test root-level component search using default tree."""
        # Set up custom tree with test data
        tree = abs.get_default_tree()
        for entity in [self.entity1, self.entity2, self.entity3]:
            tree.nodes[entity.ecs_id] = entity
        
        # Test finding entities with 'health' component using default tree
        health_entities = abs.find_entities_with_component("health")
        self.assertEqual(len(health_entities), 2)
        self.assertIn(self.entity1.ecs_id, health_entities)
        self.assertIn(self.entity2.ecs_id, health_entities)
        
        # Test finding entities with 'item' component
        item_entities = abs.find_entities_with_component("item")
        self.assertEqual(len(item_entities), 1)
        self.assertIn(self.entity3.ecs_id, item_entities)

    def test_find_entities_with_component_explicit_tree(self):
        """Test root-level component search with explicit tree parameter."""
        # Create explicit tree
        explicit_root = abs.Entity()
        explicit_tree = abs.EntityTree(
            root_ecs_id=explicit_root.ecs_id,
            lineage_id=explicit_root.lineage_id
        )
        explicit_tree.nodes[explicit_root.ecs_id] = explicit_root
        explicit_tree.nodes[self.entity1.ecs_id] = self.entity1
        
        # Test with explicit tree parameter
        health_entities = abs.find_entities_with_component("health", explicit_tree)
        self.assertEqual(len(health_entities), 1)
        self.assertIn(self.entity1.ecs_id, health_entities)
        
        # Verify default tree is not affected
        default_health = abs.find_entities_with_component("health")
        self.assertNotEqual(len(default_health), len(health_entities))

    def test_find_entities_by_relationship_default_tree(self):
        """Test root-level relationship search using default tree."""
        # Set up relationships in default tree
        tree = abs.get_default_tree()
        tree.nodes[self.entity1.ecs_id] = self.entity1
        tree.nodes[self.entity2.ecs_id] = self.entity2
        
        # Add relationship edge
        edge = abs.EntityEdge(
            source_id=self.entity1.ecs_id,
            target_id=self.entity2.ecs_id,
            edge_type=abs.EdgeType.COMPOSITION,
            field_name="equipment"
        )
        tree.edges[(self.entity1.ecs_id, self.entity2.ecs_id)] = edge
        
        # Test finding relationships using default tree
        targets = abs.find_entities_by_relationship(
            self.entity1.ecs_id, abs.EdgeType.COMPOSITION
        )
        self.assertEqual(len(targets), 1)
        self.assertIn(self.entity2.ecs_id, targets)

    def test_find_entities_by_relationship_explicit_tree(self):
        """Test root-level relationship search with explicit tree parameter."""
        # Create explicit tree with relationship
        explicit_root = abs.Entity()
        explicit_tree = abs.EntityTree(
            root_ecs_id=explicit_root.ecs_id,
            lineage_id=explicit_root.lineage_id
        )
        explicit_tree.nodes[explicit_root.ecs_id] = explicit_root
        explicit_tree.nodes[self.entity1.ecs_id] = self.entity1
        explicit_tree.nodes[self.entity3.ecs_id] = self.entity3
        
        # Add relationship
        edge = abs.EntityEdge(
            source_id=self.entity1.ecs_id,
            target_id=self.entity3.ecs_id,
            edge_type=abs.EdgeType.AGGREGATION,
            field_name="inventory"
        )
        explicit_tree.edges[(self.entity1.ecs_id, self.entity3.ecs_id)] = edge
        
        # Test with explicit tree
        targets = abs.find_entities_by_relationship(
            self.entity1.ecs_id, abs.EdgeType.AGGREGATION, explicit_tree
        )
        self.assertEqual(len(targets), 1)
        self.assertIn(self.entity3.ecs_id, targets)

    def test_root_level_functions_return_types(self):
        """Test that root-level functions return correct types."""
        # Test component search return type
        result = abs.find_entities_with_component("health")
        self.assertIsInstance(result, list)
        
        # Test relationship search return type
        result = abs.find_entities_by_relationship(
            uuid4(), abs.EdgeType.COMPOSITION
        )
        self.assertIsInstance(result, list)

    def tearDown(self):
        """Clean up after each test."""
        # Reset default tree
        abs.set_default_tree(None)


if __name__ == "__main__":
    unittest.main()