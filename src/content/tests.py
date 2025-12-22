# content/tests.py

from rest_framework.test import APITestCase
from django.test import override_settings
from unittest.mock import patch
from types import SimpleNamespace
from django.urls import reverse
from django.contrib.auth.models import User
from content.models import (
    Article,
    Book,
    Dissertation,
    ArticleCategory,
    BookCategory,
    DissertationCategory,
)
from datetime import date
from django.core.files.uploadedfile import SimpleUploadedFile


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class ContentAPITestCase(APITestCase):
    def setUp(self):
        # Создаём пользователя
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

        # ВАЖНО: используем force_authenticate — иначе is_bookmarked = False!
        self.client.force_authenticate(user=self.user)

        # Категории
        self.article_cat = ArticleCategory.objects.create(name="Ylym")
        self.book_main_cat = BookCategory.objects.create(name="Ylym kitaplary")
        self.book_sub_cat = BookCategory.objects.create(
            name="Biologiýa", parent=self.book_main_cat
        )
        self.diss_main_cat = DissertationCategory.objects.create(
            name="Doktorluk işleri"
        )
        self.diss_sub_cat = DissertationCategory.objects.create(
            name="Fizika", parent=self.diss_main_cat
        )

        # Статья
        self.article = Article.objects.create(
            title="Test Makala",
            content="<p>Bu test makalasy.</p>",
            author="Aşyr Gurbanow",
            author_workplace="TDÝ",
            average_rating=4.7,
            rating_count=12,
            views=156,
            language="tm",
            type="local",
            publication_date=date(2025, 3, 20),
        )
        self.article.categories.add(self.article_cat)
        self.user.profile.bookmarked_articles.add(self.article)  # Закладка

        # Книга
        self.book = Book.objects.create(
            title="Test Kitap",
            author="Myrat Annagurban",
            average_rating=4.3,
            rating_count=8,
            views=89,
            language="tm",
            content="Test content",
            epub_file=SimpleUploadedFile(
                "test.epub", b"file", content_type="application/epub+zip"
            ),
            cover_image=SimpleUploadedFile(
                "cover.jpg", b"img", content_type="image/jpeg"
            ),
        )
        self.book.categories.add(self.book_sub_cat)
        self.user.profile.bookmarked_books.add(self.book)

        # Диссертация
        self.dissertation = Dissertation.objects.create(
            title="Test Dissertasiýa",
            content="Dissertasiýa mazmuny...",
            author="Gülälek Berdiyeva",
            author_workplace="Ylymlar akademiýasy",
            average_rating=4.9,
            rating_count=5,
            views=42,
            language="tm",
            publication_date=date(2025, 1, 10),
        )
        self.dissertation.categories.add(self.diss_sub_cat)
        self.user.profile.bookmarked_dissertations.add(self.dissertation)

        # --- Patch search / ES / indexing to avoid external dependency ---
        # patch search_utils.index_object and delete_object so Celery tasks don't hit ES
        self.index_patcher = patch(
            "content.search_utils.index_object", return_value=True
        )
        self.delete_patcher = patch(
            "content.search_utils.delete_object", return_value=True
        )
        self.get_es_patcher = patch("content.search_utils.get_es_client")

        self.mock_index = self.index_patcher.start()
        self.mock_delete = self.delete_patcher.start()

        # Build a fake ES client that returns our DB objects in search results
        def fake_search(index=None, body=None):
            # simple behaviour: return all three objects for any query,
            # but filter by index if provided in query params
            hits = []
            if "articles" in (index or "articles,books,dissertations"):
                hits.append(
                    {
                        "_index": "articles",
                        "_id": str(self.article.id),
                        "_source": {
                            "title": self.article.title,
                            "author": self.article.author,
                            "language": self.article.language,
                            "average_rating": float(self.article.average_rating),
                            "rating_count": self.article.rating_count,
                            "views": self.article.views,
                            "content": self.article.content,
                            "categories": [
                                {
                                    "id": self.article_cat.id,
                                    "name": self.article_cat.name,
                                }
                            ],
                        },
                    }
                )
            if "books" in (index or "articles,books,dissertations"):
                hits.append(
                    {
                        "_index": "books",
                        "_id": str(self.book.id),
                        "_source": {
                            "title": self.book.title,
                            "author": self.book.author,
                            "language": self.book.language,
                            "average_rating": float(self.book.average_rating),
                            "rating_count": self.book.rating_count,
                            "views": self.book.views,
                            "content": getattr(self.book, "content", None),
                            "categories": [
                                {
                                    "id": self.book_sub_cat.id,
                                    "name": self.book_sub_cat.name,
                                }
                            ],
                        },
                    }
                )
            if "dissertations" in (index or "articles,books,dissertations"):
                hits.append(
                    {
                        "_index": "dissertations",
                        "_id": str(self.dissertation.id),
                        "_source": {
                            "title": self.dissertation.title,
                            "author": self.dissertation.author,
                            "language": self.dissertation.language,
                            "average_rating": float(self.dissertation.average_rating),
                            "rating_count": self.dissertation.rating_count,
                            "views": self.dissertation.views,
                            "content": self.dissertation.content,
                            "categories": [
                                {
                                    "id": self.diss_sub_cat.id,
                                    "name": self.diss_sub_cat.name,
                                }
                            ],
                        },
                    }
                )

            return {"hits": {"total": {"value": len(hits)}, "hits": hits}}

        fake_client = SimpleNamespace(search=fake_search)
        mocked_get_es = self.get_es_patcher.start()
        mocked_get_es.return_value = fake_client

    # ======================= СТАТЬИ =======================
    def test_article_list(self):
        url = reverse("article-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        data = response.data["results"][0]
        self.assertEqual(data["title"], "Test Makala")
        self.assertTrue(data["is_bookmarked"])
        self.assertEqual(data["average_rating"], 4.7)
        self.assertEqual(data["categories"][0]["name"], "Ylym")

    def test_article_detail(self):
        url = reverse("article-detail", kwargs={"pk": self.article.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Test Makala")
        self.assertTrue(response.data["is_bookmarked"])

    def test_article_filters(self):
        tests = [
            ("?language=tm", 1),
            ("?type=local", 1),
            (f"?categories={self.article_cat.id}", 1),
            ("?publication_date__gte=2025-01-01", 1),
            ("?publication_date__lte=2025-12-31", 1),
        ]
        for query, expected_count in tests:
            with self.subTest(query=query):
                response = self.client.get(reverse("article-list") + query)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(response.data["results"]), expected_count)

    # ======================= КНИГИ =======================
    def test_book_list(self):
        url = reverse("book-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        data = response.data["results"][0]
        self.assertEqual(data["title"], "Test Kitap")
        self.assertTrue(data["is_bookmarked"])
        self.assertEqual(data["average_rating"], 4.3)
        self.assertIn("Biologiýa", [c["name"] for c in data["categories"]])

    def test_book_detail(self):
        url = reverse("book-detail", kwargs={"pk": self.book.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_bookmarked"])
        self.assertIsNotNone(response.data["epub_file"])

    def test_book_filters(self):
        response = self.client.get(
            reverse("book-list") + f"?categories={self.book_sub_cat.id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

        response = self.client.get(reverse("book-list") + "?language=tm")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    # ======================= ДИССЕРТАЦИИ =======================
    def test_dissertation_list(self):
        url = reverse("dissertation-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        data = response.data["results"][0]
        self.assertEqual(data["title"], "Test Dissertasiýa")
        self.assertTrue(data["is_bookmarked"])
        self.assertEqual(data["average_rating"], 4.9)

    def test_dissertation_detail(self):
        url = reverse("dissertation-detail", kwargs={"pk": self.dissertation.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_bookmarked"])

    def test_dissertation_filters(self):
        response = self.client.get(reverse("dissertation-list") + "?language=tm")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

        response = self.client.get(
            reverse("dissertation-list") + f"?categories={self.diss_sub_cat.id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    # ======================= КАТЕГОРИИ =======================
    def test_category_lists(self):
        # Article categories
        response = self.client.get(reverse("articlecategory-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Ylym")

        # Book categories
        response = self.client.get(reverse("bookcategory-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

        # Book category with parent filter
        response = self.client.get(
            reverse("bookcategory-list") + f"?parent={self.book_main_cat.id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Biologiýa")

        # Dissertation categories
        response = self.client.get(reverse("dissertationcategory-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_elasticsearch_integration_category(self):
        try:
            response = self.client.get(reverse("content-search") + "?category=Ylym")
            self.assertEqual(response.status_code, 200)
            self.assertGreaterEqual(len(response.data["results"]), 1)
        except Exception as e:
            self.fail(f"Elasticsearch integration test failed: {e}")

    def test_elasticsearch_integration_content_type(self):
        try:
            response = self.client.get(reverse("content-search") + "?content_type=book")
            self.assertEqual(response.status_code, 200)
            self.assertGreaterEqual(len(response.data["results"]), 1)
        except Exception as e:
            self.fail(f"Elasticsearch integration test failed: {e}")

    def test_elasticsearch_integration_title(self):
        try:
            response = self.client.get(reverse("content-search") + "?title=Test Makala")
            self.assertEqual(response.status_code, 200)
            self.assertGreaterEqual(len(response.data["results"]), 1)
        except Exception as e:
            self.fail(f"Elasticsearch integration test failed: {e}")

    def test_elasticsearch_integration_fulltext(self):
        try:
            response = self.client.get(reverse("content-search") + "?q=test")
            self.assertEqual(response.status_code, 200)
            self.assertGreaterEqual(len(response.data["results"]), 1)
        except Exception as e:
            self.fail(f"Elasticsearch integration test failed: {e}")

    def test_elasticsearch_integration_publication_date_range(self):
        try:
            response = self.client.get(
                reverse("content-search")
                + "?publication_date__gte=2025-01-01&publication_date__lte=2025-12-31"
            )
            self.assertEqual(response.status_code, 200)
            self.assertGreaterEqual(len(response.data["results"]), 1)
        except Exception as e:
            self.fail(f"Elasticsearch integration test failed: {e}")

    def tearDown(self):
        try:
            self.index_patcher.stop()
            self.delete_patcher.stop()
            self.get_es_patcher.stop()
        except Exception:
            pass
