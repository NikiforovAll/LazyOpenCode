# Testing Guidelines

Standards for writing and organizing tests in this project.

## Test Structure

Use descriptive test names that explain what is being tested:

```typescript
describe('UserService', () => {
  describe('getUserById', () => {
    it('should return user when user exists', async () => {
      // test
    });

    it('should throw NotFoundError when user does not exist', async () => {
      // test
    });
  });
});
```

## Test Coverage

Aim for at least 80% code coverage:
- Critical paths: 100%
- Business logic: 90%+
- Utilities: 80%+
- Skip trivial getters/setters

## Mocking and Fixtures

Use fixtures for common test data:
```typescript
const mockUser = {
  id: '123',
  name: 'John Doe',
  email: 'john@example.com'
};
```

Mock external dependencies:
- Database calls
- API requests
- File system operations
- Third-party services

## Async Testing

Always use `async/await` for async tests:

```typescript
it('should fetch user data', async () => {
  const user = await userService.getUser('123');
  expect(user.name).toBe('John Doe');
});
```

## Performance Tests

Mark performance-critical tests with a timeout:

```typescript
it('should process large datasets efficiently', async () => {
  // This test should complete within 5 seconds
  jest.setTimeout(5000);
  const result = await processor.process(largeDataset);
  expect(result).toBeDefined();
}, 5000);
```
