# API Examples

Collection of common API usage examples for SMU Digital Library.

## Authentication

### Register New User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
  }'
```

**Response:**

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com"
}
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123!"
  }'
```

**Response:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Refresh Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

## Content Retrieval

### List Articles

```bash
# Simple list
curl http://localhost:8000/api/v1/articles/

# With pagination
curl http://localhost:8000/api/v1/articles/?page=2

# Filter by language
curl http://localhost:8000/api/v1/articles/?language=tm

# Filter by date range
curl "http://localhost:8000/api/v1/articles/?publication_date__gte=2024-01-01&publication_date__lte=2024-12-31"

# Multiple filters
curl "http://localhost:8000/api/v1/articles/?language=en&type=foreign"
```

### Get Article Details

```bash
curl http://localhost:8000/api/v1/articles/123/
```

### List Books

```bash
# All books
curl http://localhost:8000/api/v1/books/

# Filter by category
curl http://localhost:8000/api/v1/books/?categories=5

# Filter by language
curl http://localhost:8000/api/v1/books/?language=ru
```

### List Dissertations

```bash
curl http://localhost:8000/api/v1/dissertations/

# With filters
curl "http://localhost:8000/api/v1/dissertations/?language=tm&publication_date__gte=2023-01-01"
```

## Search

### Basic Search

```bash
# Search across all content
curl "http://localhost:8000/api/v1/search/?q=machine+learning"
```

**Response:**

```json
{
  "count": 15,
  "page": 1,
  "page_size": 8,
  "has_next": true,
  "query": "machine learning",
  "results": [
    {
      "id": 42,
      "content_type": "article",
      "title": "Introduction to Machine Learning",
      "author": "John Smith",
      "language": "en",
      "average_rating": 4.5,
      "rating_count": 10,
      "views": 350,
      "score": 12.5,
      "highlight": {
        "title": ["Introduction to <mark>Machine</mark> <mark>Learning</mark>"],
        "content": [
          "... basics of <mark>machine</mark> <mark>learning</mark> algorithms ..."
        ]
      }
    }
  ]
}
```

### Advanced Search with Filters

```bash
# Search only in articles
curl "http://localhost:8000/api/v1/search/?q=science&content_type=article"

# Search with language filter
curl "http://localhost:8000/api/v1/search/?q=технология&language=ru"

# Search by author
curl "http://localhost:8000/api/v1/search/?author=Smith"

# Search with date range
curl "http://localhost:8000/api/v1/search/?q=AI&publication_date__gte=2024-01-01"

# Search by category
curl "http://localhost:8000/api/v1/search/?category_id=3"

# Complex query
curl "http://localhost:8000/api/v1/search/?q=neural+networks&content_type=article&language=en&publication_date__gte=2023-01-01&page=1"
```

## User Interactions (Requires Authentication)

### Add/Remove Bookmark

```bash
# Add bookmark
curl -X POST http://localhost:8000/api/v1/bookmarks/toggle/123/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "article"
  }'
```

**Response:**

```json
{
  "added": true,
  "is_bookmarked": true
}
```

### Get User Bookmarks

```bash
curl http://localhost:8000/api/v1/bookmarks/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**

```json
{
  "articles": [
    {
      "id": 123,
      "title": "Article Title",
      "author": "Author Name",
      "average_rating": 4.5,
      "views": 100
    }
  ],
  "books": [...],
  "dissertations": [...]
}
```

### Rate Content

```bash
curl -X POST http://localhost:8000/api/v1/rate/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "article",
    "content_id": 123,
    "rating": 5
  }'
```

**Response:**

```json
{
  "success": true,
  "message": "Rating created",
  "rating": 5
}
```

### Register View

```bash
curl -X POST http://localhost:8000/api/v1/views/article/123/ \
  -H "Content-Type: application/json"
```

**Response:**

```json
{
  "accepted": true
}
```

## Categories

### List Article Categories

```bash
curl http://localhost:8000/api/v1/article-categories/
```

### List Book Categories

```bash
# All categories
curl http://localhost:8000/api/v1/book-categories/

# Only top-level categories
curl http://localhost:8000/api/v1/book-categories/?parent__isnull=true

# Children of specific category
curl http://localhost:8000/api/v1/book-categories/?parent=5
```

## Python Examples

### Using requests library

```python
import requests

API_BASE = "http://localhost:8000/api/v1"

# Login
response = requests.post(f"{API_BASE}/auth/login/", json={
    "username": "john_doe",
    "password": "SecurePass123!"
})
tokens = response.json()
access_token = tokens["access"]

# Get articles with authentication
headers = {"Authorization": f"Bearer {access_token}"}
articles = requests.get(f"{API_BASE}/articles/", headers=headers)
print(articles.json())

# Search
search_results = requests.get(f"{API_BASE}/search/", params={
    "q": "machine learning",
    "language": "en"
})
print(search_results.json())

# Add bookmark
bookmark_response = requests.post(
    f"{API_BASE}/bookmarks/toggle/123/",
    headers=headers,
    json={"type": "article"}
)
print(bookmark_response.json())
```

## JavaScript/Fetch Examples

```javascript
const API_BASE = "http://localhost:8000/api/v1";

// Login
async function login(username, password) {
  const response = await fetch(`${API_BASE}/auth/login/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  });

  const data = await response.json();
  localStorage.setItem("access_token", data.access);
  localStorage.setItem("refresh_token", data.refresh);
  return data;
}

// Get articles
async function getArticles(filters = {}) {
  const params = new URLSearchParams(filters);
  const response = await fetch(`${API_BASE}/articles/?${params}`);
  return await response.json();
}

// Search
async function search(query, filters = {}) {
  const params = new URLSearchParams({ q: query, ...filters });
  const response = await fetch(`${API_BASE}/search/?${params}`);
  return await response.json();
}

// Toggle bookmark (authenticated)
async function toggleBookmark(id, type) {
  const token = localStorage.getItem("access_token");
  const response = await fetch(`${API_BASE}/bookmarks/toggle/${id}/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ type }),
  });
  return await response.json();
}

// Usage
login("john_doe", "SecurePass123!")
  .then(() => getArticles({ language: "en", page: 1 }))
  .then((data) => console.log(data));
```

## Error Handling

### Example Error Response

```json
{
  "error": true,
  "status_code": 400,
  "message": "content_type, content_id, and rating are required",
  "details": {
    "content_type": ["This field is required."]
  }
}
```

### Common Error Codes

- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable (e.g., Elasticsearch down)

## Rate Limiting

### Headers in Response

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640000000
```

### Rate Limits

| Endpoint Type | Anonymous | Authenticated |
| ------------- | --------- | ------------- |
| General       | 100/hour  | 1000/hour     |
| Search        | 30/minute | 30/minute     |
| Auth          | 5/minute  | N/A           |

## Tips & Best Practices

1. **Always use HTTPS in production**
2. **Store tokens securely** (httpOnly cookies recommended)
3. **Refresh tokens before expiry** (60 minutes for access tokens)
4. **Handle rate limiting** (implement exponential backoff)
5. **Cache responses** when appropriate
6. **Use pagination** for large datasets
7. **Filter on backend** rather than client-side

## Testing with cURL

### Save credentials

```bash
# Save token to file
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}' \
  | jq -r '.access' > token.txt

# Use token from file
TOKEN=$(cat token.txt)
curl http://localhost:8000/api/v1/bookmarks/ \
  -H "Authorization: Bearer $TOKEN"
```

### Pretty print JSON

```bash
curl http://localhost:8000/api/v1/articles/ | jq .
```

---

For more examples, see:

- [API Documentation](http://localhost:8000/api/docs/swagger/)
- [README.md](README.md)
- [Tests](src/content/tests.py)
