## Context

The repository has implemented multiple features across backend (Django) and frontend (Vue), but test coverage is sparse. Existing tests are placeholder stubs or minimal integration tests. This change establishes a systematic testing approach.

## Goals

1. **Unit Test Coverage**: 80%+ for backend services, serializers, and utilities
2. **Integration Test Coverage**: All API endpoints covered
3. **E2E Coverage**: Critical user flows verified end-to-end
4. **CI Integration**: Tests run automatically on PR/merge

## Design

### Testing Pyramid

```
        E2E Tests (few, slow, high confidence)
       /                                  \
      /    Integration Tests (medium)       \
     /                                      \
    /          Unit Tests (many, fast)        \
   /                                          \
```

### Backend Testing (Django)

**Unit Tests** (`apps/*/tests.py`):
- Service layer logic
- Serializer validation
- Utility functions
- Model methods

**Integration Tests** (`apps/*/tests.py`):
- API endpoint behavior
- Database operations
- Authentication/authorization

**Framework**: pytest + pytest-django + pytest-cov

### Frontend Testing (Vue)

**Unit Tests** (`ui/src/**/*.test.ts`):
- Composable functions
- Utility functions
- Store logic

**Integration Tests** (`ui/src/**/*.test.ts`):
- Component behavior
- Store integration
- API client mocking

**Framework**: vitest + @vue/test-utils

### E2E Testing

**Critical User Flows** (`ui/e2e/`):
1. Login and authentication
2. User management (CRUD)
3. Workspace operations
4. Application creation and management
5. Knowledge base operations
6. Chat interactions

**Framework**: Playwright (chromium)

### Test Organization

```
apps/
├── users/
│   ├── tests.py           # Unit + Integration tests
│   └── conftest.py        # Fixtures
├── application/
│   ├── tests.py
│   └── conftest.py
└── common/
    └── test_utils/        # Shared test utilities

ui/
├── src/
│   └── **/*.test.ts       # Unit tests
├── e2e/
│   ├── login/
│   ├── user-management/
│   ├── workspace/
│   └── application/
└── e2e/fixtures/          # E2E test data
```

## Dependencies

- pytest, pytest-django, pytest-cov (backend)
- vitest, @vue/test-utils (frontend)
- Playwright (E2E)

## Out of Scope

- Performance testing
- Load testing
- Security penetration testing
