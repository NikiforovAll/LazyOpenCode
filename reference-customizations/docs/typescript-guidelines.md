# TypeScript Development Guidelines

Standards and best practices for TypeScript code in this project.

## Type Annotations

Always use explicit type annotations for:
- Function parameters
- Function return types
- Class properties
- Module exports

Example:
```typescript
function processData(input: string): Promise<Data[]> {
  // implementation
}
```

## Naming Conventions

- **Classes**: PascalCase (e.g., `UserManager`)
- **Functions**: camelCase (e.g., `getUserById`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`)
- **Private members**: prefix with underscore (e.g., `_internal`)

## Strict Mode

All TypeScript files must compile with strict mode enabled:
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}
```

## No `any` Type

Avoid using `any` type. Use `unknown` with type guards instead:

```typescript
// ❌ Bad
function process(data: any) {
  return data.value;
}

// ✅ Good
function process(data: unknown) {
  if (typeof data === 'object' && data !== null && 'value' in data) {
    return data.value;
  }
}
```
