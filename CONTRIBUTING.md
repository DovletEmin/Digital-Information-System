# Contributing to SMU Digital Library

Thank you for considering contributing to SMU Digital Library! This document outlines the process and guidelines.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Testing Guidelines](#testing-guidelines)

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Respect differing viewpoints

## Getting Started

1. Fork the repository
2. Clone your fork:

   ```bash
   git clone https://github.com/yourusername/smu-library.git
   cd smu-library
   ```

3. Add upstream remote:

   ```bash
   git remote add upstream https://github.com/original/smu-library.git
   ```

4. Create a development environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   make build
   make up
   ```

## Development Workflow

1. **Create a feature branch**:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write code following our standards
   - Add tests for new functionality
   - Update documentation

3. **Run tests and linters**:

   ```bash
   make test
   make lint
   ```

4. **Commit your changes**:

   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

5. **Push to your fork**:

   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request**

## Coding Standards

### Python Code Style

- Follow **PEP 8** style guide
- Use **type hints** for function parameters and returns
- Maximum line length: **88 characters** (Black formatter default)
- Use **docstrings** for all public functions, classes, and modules

Example:

```python
def calculate_rating(ratings: list[int], default: float = 0.0) -> float:
    """
    Calculate average rating from a list of integer ratings.

    Args:
        ratings: List of rating values (1-5)
        default: Default value if ratings list is empty

    Returns:
        Average rating as float, or default if no ratings

    Example:
        >>> calculate_rating([5, 4, 5, 3])
        4.25
    """
    if not ratings:
        return default
    return sum(ratings) / len(ratings)
```

### Django Best Practices

- Use Django ORM instead of raw SQL
- Always use `select_related()` and `prefetch_related()` for related objects
- Create indexes for frequently queried fields
- Use Django signals sparingly
- Keep business logic in models or services, not views

### API Design

- Follow RESTful principles
- Use proper HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Return appropriate status codes
- Include pagination for list endpoints
- Version your API (`/api/v1/`, `/api/v2/`)

### Testing

- Write tests for all new features
- Aim for >80% code coverage
- Use factories for test data
- Test edge cases and error conditions

Example:

```python
import pytest
from django.contrib.auth.models import User
from content.models import Article

@pytest.mark.django_db
class TestArticleAPI:
    def test_create_article(self, api_client, user):
        """Test article creation via API"""
        api_client.force_authenticate(user=user)

        response = api_client.post('/api/v1/articles/', {
            'title': 'Test Article',
            'content': 'Test content',
            'author': 'John Doe',
            'language': 'en',
        })

        assert response.status_code == 201
        assert Article.objects.count() == 1
```

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/).

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

### Examples

```
feat(api): add filtering to article list endpoint

Added support for filtering articles by publication date range.
Users can now use ?publication_date__gte and __lte parameters.

Closes #123
```

```
fix(search): handle Elasticsearch connection errors

Wrapped ES client calls in try-except to prevent 500 errors
when Elasticsearch is temporarily unavailable.
```

## Pull Request Process

1. **Update Documentation**: Ensure README and docs are updated if needed

2. **Add Tests**: All new features must have tests

3. **Pass CI Checks**: Ensure all automated checks pass

4. **Update CHANGELOG**: Add your changes under "Unreleased"

5. **Request Review**: Tag at least one maintainer for review

6. **Address Feedback**: Make requested changes promptly

7. **Squash Commits**: Keep PR history clean (optional)

### PR Template

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Updated existing tests

## Checklist

- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] No new warnings
- [ ] Added tests
- [ ] All tests pass
```

## Testing Guidelines

### Running Tests

```bash
# All tests
make test

# With coverage
make test-cov

# Specific test file
docker-compose exec web pytest src/content/tests/test_api.py

# Specific test
docker-compose exec web pytest src/content/tests/test_api.py::TestArticleAPI::test_create_article
```

### Writing Tests

1. **Use pytest fixtures**:

```python
@pytest.fixture
def article(db):
    return Article.objects.create(
        title="Test Article",
        content="Test content",
        author="Test Author",
    )
```

2. **Test different scenarios**:

- Happy path (success case)
- Error cases
- Edge cases
- Permission checks

3. **Keep tests isolated**:

- Don't depend on other tests
- Clean up after yourself
- Use transactions/rollback

## Documentation

### Docstring Style

Use Google-style docstrings:

```python
def function(arg1: str, arg2: int) -> bool:
    """
    Short description of function.

    Longer description if needed, explaining what the function does
    in more detail.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: When arg2 is negative

    Example:
        >>> function("test", 5)
        True
    """
```

### API Documentation

- Use drf-yasg decorators for Swagger docs
- Include example requests/responses
- Document all parameters
- Specify required fields

## Questions?

Feel free to open an issue for:

- Questions about contributing
- Clarification on guidelines
- Suggestions for improvements

Thank you for contributing! 🎉
