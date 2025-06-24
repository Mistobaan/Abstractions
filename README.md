# Abstractions

A Python library for building and managing entity graphs with versioning, immutability, and serialization support.

## Features

- **Entity System**: Pydantic-based entities with automatic ID management
- **Graph Construction**: Automatic graph building from entity relationships
- **Versioning**: Track entity changes with hierarchical propagation
- **Immutability**: Deep copy-based immutability for safe entity retrieval
- **Serialization**: JSON serialization/deserialization support
- **Entity Registry**: Storage and retrieval system with version tracking

## Quick Start

```python
from abstractions.ecs.entity import Entity, EntityRegistry, build_entity_graph

# Define your entities
class User(Entity):
    name: str = ""
    email: str = ""

class Project(Entity):
    title: str = ""
    owner: User = None
    collaborators: List[User] = []

# Create entities
user1 = User(name="Alice", email="alice@example.com")
user2 = User(name="Bob", email="bob@example.com")

project = Project(
    title="My Project",
    owner=user1,
    collaborators=[user2]
)

# Build entity graph
graph = build_entity_graph(project)
print(f"Graph has {len(graph.nodes)} entities and {len(graph.edges)} relationships")

# Use registry for storage and versioning
registry = EntityRegistry()
registry.register_entity_graph(graph)

# Retrieve and modify entities
retrieved_project = registry.get_stored_entity(project.ecs_id, project.root_ecs_id)
retrieved_project.title = "Updated Project"

# Version the changes
registry.version_entity(retrieved_project)
```

## Testing

Run tests with coverage:

```bash
make coverage
```

## Documentation

See `CLAUDE.md` for detailed implementation documentation and development guidelines.
