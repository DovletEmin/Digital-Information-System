"""
Search functionality for API v1 with improved error handling.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.core.cache import cache
from elasticsearch import Elasticsearch
import logging
from datetime import datetime

from content.utils.throttles import SearchRateThrottle

logger = logging.getLogger(__name__)


class ElasticsearchClient:
    """Singleton pattern for Elasticsearch client"""

    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_client(self):
        """Get or create Elasticsearch client"""
        if self._client is None:
            try:
                es_url = settings.ELASTICSEARCH_DSL["default"]["hosts"]
                self._client = Elasticsearch(es_url, timeout=30)
            except Exception as e:
                logger.error(f"Failed to create Elasticsearch client: {e}")
                self._client = None
        return self._client

    def ping(self):
        """Check if Elasticsearch is available"""
        cache_key = "es_ping_ok"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            client = self.get_client()
            ok = bool(client and client.ping())
        except Exception:
            ok = False

        cache.set(cache_key, ok, 5)
        return ok


es_client = ElasticsearchClient()


class ContentSearchView(APIView):
    """
    Full-text search across all content types using Elasticsearch.
    Implements caching and proper error handling.
    """

    # throttle_classes = [SearchRateThrottle]

    def get(self, request):
        """Handle search requests"""
        q = request.query_params.get("q", "").strip()
        page = max(int(request.query_params.get("page", 1)), 1)
        page_size = settings.REST_FRAMEWORK["PAGE_SIZE"]
        from_ = (page - 1) * page_size

        # Check cache first
        try:
            version = int(cache.get("content_cache_version") or 0)
        except Exception:
            version = 0

        cache_key = f"search:v{version}:{request.get_full_path()}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        # Check Elasticsearch availability
        client = es_client.get_client()
        if not es_client.ping():
            return Response(
                {
                    "error": "Search service temporarily unavailable",
                    "message": "Please try again later",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Build search query
        body = self._build_search_body(request, q, from_, page_size)

        # Execute search
        try:
            response = client.search(index="articles,books,dissertations", body=body)
        except Exception as e:
            logger.error(f"Elasticsearch search error: {e}")
            return Response(
                {
                    "error": "Search error occurred",
                    "message": "An error occurred while searching. Please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Process results
        results = self._process_results(response)

        resp_data = {
            "count": response["hits"]["total"]["value"],
            "page": page,
            "page_size": page_size,
            "has_next": len(results) == page_size,
            "results": results,
            "query": q,
        }

        # Cache results
        try:
            cache.set(cache_key, resp_data, 300)
        except Exception:
            pass

        return Response(resp_data)

    def _build_search_body(self, request, query, from_, size):
        """Build Elasticsearch query body"""
        body = {
            "from": from_,
            "size": size,
            "query": {"bool": {"must": [], "filter": []}},
            "_source": [
                "title",
                "author",
                "language",
                "average_rating",
                "rating_count",
                "views",
                "publication_date",
                "image",
                "epub_file",
                "cover_image",
                "source_name",
                "source_url",
                "newspaper_or_journal",
                "author_workplace",
                "type",
                "categories",
            ],
            "highlight": {
                "pre_tags": ["<mark>"],
                "post_tags": ["</mark>"],
                "fields": {
                    "title": {"fragment_size": 100, "number_of_fragments": 1},
                    "content": {"fragment_size": 120, "number_of_fragments": 1},
                },
            },
            "sort": [{"_score": {"order": "desc"}}],
        }

        # Add search query
        if query:
            body["query"]["bool"]["must"].append(
                {
                    "multi_match": {
                        "query": query,
                        "fields": [
                            "title^10",
                            "content^3",
                            "author^5",
                            "author_workplace^2",
                            "source_name^2",
                            "newspaper_or_journal^2",
                        ],
                        "type": "best_fields",
                        "fuzziness": "AUTO",
                    }
                }
            )
        else:
            body["query"]["bool"]["must"].append({"match_all": {}})

        # Add filters
        filters = self._build_filters(request)
        if filters:
            body["query"]["bool"]["filter"] = filters

        # Adjust sorting for non-search queries
        if not query:
            body["sort"].insert(0, {"average_rating": {"order": "desc"}})
            body["sort"].append({"views": {"order": "desc"}})

        return body

    def _build_filters(self, request):
        """Build filter clauses from request parameters"""
        filters = []

        # Content type filter
        content_type = request.query_params.get("content_type")
        if content_type in ["article", "book", "dissertation"]:
            filters.append({"term": {"_index": f"{content_type}s"}})

        # Language filter
        if request.query_params.get("language"):
            filters.append(
                {"term": {"language.keyword": request.query_params["language"]}}
            )

        # Type filter (for articles)
        if request.query_params.get("type"):
            filters.append({"term": {"type.keyword": request.query_params["type"]}})

        # Author filter
        if request.query_params.get("author"):
            filters.append({"term": {"author.keyword": request.query_params["author"]}})

        # Date filters
        if request.query_params.get("publication_date"):
            filters.append(
                {"term": {"publication_date": request.query_params["publication_date"]}}
            )

        if request.query_params.get("publication_date__gte"):
            filters.append(
                {
                    "range": {
                        "publication_date": {
                            "gte": request.query_params["publication_date__gte"]
                        }
                    }
                }
            )

        if request.query_params.get("publication_date__lte"):
            filters.append(
                {
                    "range": {
                        "publication_date": {
                            "lte": request.query_params["publication_date__lte"]
                        }
                    }
                }
            )

        # Category filters
        if request.query_params.get("category_id"):
            try:
                category_id = int(request.query_params["category_id"])
                filters.append(
                    {
                        "nested": {
                            "path": "categories",
                            "query": {"term": {"categories.id": category_id}},
                        }
                    }
                )
            except ValueError:
                pass

        if request.query_params.get("category_name"):
            filters.append(
                {
                    "nested": {
                        "path": "categories",
                        "query": {
                            "match": {
                                "categories.name": request.query_params["category_name"]
                            }
                        },
                    }
                }
            )

        return filters

    def _process_results(self, response):
        """Process Elasticsearch results"""
        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            index_name = hit["_index"]
            content_type = index_name.rstrip("s")

            base = {
                "id": int(hit["_id"]),
                "content_type": content_type,
                "title": source.get("title", "Untitled"),
                "author": source.get("author", "Unknown"),
                "language": source.get("language", "tm"),
                "average_rating": round(float(source.get("average_rating", 0)), 2),
                "rating_count": source.get("rating_count", 0),
                "views": source.get("views", 0),
                "score": hit.get("_score", 0),
                "highlight": hit.get("highlight", {}),
            }

            # Add type-specific fields
            if content_type == "article":
                base.update(
                    {
                        "author_workplace": source.get("author_workplace"),
                        "type": source.get("type"),
                        "publication_date": self._format_date(
                            source.get("publication_date")
                        ),
                        "source_name": source.get("source_name"),
                        "source_url": source.get("source_url"),
                        "newspaper_or_journal": source.get("newspaper_or_journal"),
                        "image": source.get("image"),
                    }
                )
            elif content_type == "book":
                base.update(
                    {
                        "epub_file": source.get("epub_file"),
                        "cover_image": source.get("cover_image"),
                    }
                )
            elif content_type == "dissertation":
                base.update(
                    {
                        "author_workplace": source.get("author_workplace"),
                        "publication_date": self._format_date(
                            source.get("publication_date")
                        ),
                    }
                )

            base["categories"] = source.get("categories", [])
            results.append(base)

        return results

    @staticmethod
    def _format_date(date_str):
        """Format date string to DD.MM.YYYY"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str.split("T")[0], "%Y-%m-%d").strftime(
                "%d.%m.%Y"
            )
        except Exception:
            return date_str.split("T")[0] if date_str else None
