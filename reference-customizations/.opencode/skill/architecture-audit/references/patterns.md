# Architectural Patterns

## Layered Architecture
- **API Layer**: Handles HTTP requests.
- **Service Layer**: Contains business logic.
- **Data Layer**: Database abstractions.

## Prohibited Dependencies
- Data layer must NEVER import from Service or API layer.
- Service layer must NEVER import from API layer.
