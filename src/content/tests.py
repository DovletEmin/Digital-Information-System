from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import (
    Article,
    Book,
    Dissertation,
    ArticleCategory,
    BookCategory,
    DissertationCategory,
)
from datetime import date
from django.core.files.uploadedfile import SimpleUploadedFile


class APITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")

        self.article_category = ArticleCategory.objects.create(name="Science")
        self.book_top_category = BookCategory.objects.create(name="Scientific")
        self.book_subcategory = BookCategory.objects.create(
            name="Biology", parent=self.book_top_category
        )
        self.dissertation_top_category = DissertationCategory.objects.create(
            name="Academic"
        )
        self.dissertation_subcategory = DissertationCategory.objects.create(
            name="Physics", parent=self.dissertation_top_category
        )

        self.article = Article.objects.create(
            title="Test Article",
            content="Article content",
            author="John Doe",
            author_workplace="University",
            rating=4.5,
            views=100,
            language="tm",
            type="local",
            publication_date=date(2023, 1, 1),
            source_name="Test Source",
            source_url="http://example.com",
            newspaper_or_journal="Test Journal",
        )
        self.article.categories.add(self.article_category)
        self.article.bookmarks.add(self.user)

        self.book = Book.objects.create(
            title="Test Book",
            content="Book content",
            epub_file=SimpleUploadedFile("test.epub", b"file_content"),
            cover_image=SimpleUploadedFile("test.jpg", b"image_content"),
            author="Jane Doe",
            rating=3.8,
            views=50,
            language="ru",
        )
        self.book.categories.add(self.book_subcategory)
        self.book.bookmarks.add(self.user)

        self.dissertation = Dissertation.objects.create(
            title="Test Dissertation",
            content="Dissertation content",
            author="Alice Smith",
            author_workplace="Institute",
            rating=4.0,
            views=30,
            language="en",
            publication_date=date(2024, 6, 15),
        )
        self.dissertation.categories.add(self.dissertation_subcategory)
        self.dissertation.bookmarks.add(self.user)

    def test_get_article_list(self):
        url = reverse("article-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Article")
        self.assertEqual(
            response.data["results"][0]["categories"][0]["name"], "Science"
        )
        self.assertEqual(response.data["results"][0]["bookmarks"], [self.user.id])

    def test_get_article_detail(self):
        url = reverse("article-detail", kwargs={"pk": self.article.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Test Article")
        self.assertEqual(response.data["language"], "tm")

    def test_article_filter_by_language(self):
        url = reverse("article-list") + "?language=tm"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["language"], "tm")

    def test_article_filter_by_type(self):
        url = reverse("article-list") + "?type=local"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["type"], "local")

    def test_article_filter_by_category(self):
        url = reverse("article-list") + f"?categories={self.article_category.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["categories"][0]["name"], "Science"
        )

    def test_article_filter_by_date_range(self):
        url = (
            reverse("article-list")
            + "?publication_date__gte=2023-01-01&publication_date__lte=2023-12-31"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["publication_date"], "2023-01-01")

    def test_article_combined_filter(self):
        url = (
            reverse("article-list")
            + f"?language=tm&type=local&categories={self.article_category.id}&publication_date__gte=2023-01-01"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Article")

    def test_get_book_list(self):
        url = reverse("book-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Book")
        self.assertEqual(
            response.data["results"][0]["categories"][0]["name"], "Biology"
        )

    def test_get_book_detail(self):
        url = reverse("book-detail", kwargs={"pk": self.book.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Test Book")
        self.assertEqual(response.data["language"], "ru")

    def test_book_filter_by_language(self):
        url = reverse("book-list") + "?language=ru"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["language"], "ru")

    def test_book_filter_by_category(self):
        url = reverse("book-list") + f"?categories={self.book_subcategory.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["categories"][0]["name"], "Biology"
        )

    def test_get_dissertation_list(self):
        url = reverse("dissertation-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Dissertation")
        self.assertEqual(
            response.data["results"][0]["categories"][0]["name"], "Physics"
        )

    def test_get_dissertation_detail(self):
        url = reverse("dissertation-detail", kwargs={"pk": self.dissertation.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Test Dissertation")
        self.assertEqual(response.data["language"], "en")

    def test_dissertation_filter_by_language(self):
        url = reverse("dissertation-list") + "?language=en"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["language"], "en")

    def test_dissertation_filter_by_category(self):
        url = (
            reverse("dissertation-list")
            + f"?categories={self.dissertation_subcategory.id}"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["categories"][0]["name"], "Physics"
        )

    def test_get_article_category_list(self):
        url = reverse("articlecategory-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Science")

    def test_get_book_category_list(self):
        url = reverse("bookcategory-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["name"], "Scientific")

    def test_book_category_filter_by_parent(self):
        url = reverse("bookcategory-list") + f"?parent={self.book_top_category.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Biology")

    def test_book_category_filter_by_top_level(self):
        url = reverse("bookcategory-list") + "?parent__isnull=true"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Scientific")

    def test_get_dissertation_category_list(self):
        url = reverse("dissertationcategory-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["name"], "Academic")

    def test_dissertation_category_filter_by_parent(self):
        url = (
            reverse("dissertationcategory-list")
            + f"?parent={self.dissertation_top_category.id}"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Physics")

    def test_dissertation_category_filter_by_top_level(self):
        url = reverse("dissertationcategory-list") + "?parent__isnull=true"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Academic")
