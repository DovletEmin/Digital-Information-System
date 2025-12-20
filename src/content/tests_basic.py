from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from content.models import Article, Book, Dissertation, ContentRating
from datetime import date


class BookmarkAndRatingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tb", password="pw12345")
        self.client.force_authenticate(user=self.user)

        self.article = Article.objects.create(
            title="Tb article",
            content="x",
            author="a",
            publication_date=date(2025, 1, 1),
            language="tm",
        )

    def test_toggle_bookmark_article(self):
        url = reverse("toggle-bookmark", kwargs={"pk": self.article.pk})
        # add
        resp = self.client.post(url, {"type": "article"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data.get("added"))

        # toggle off
        resp = self.client.post(url, {"type": "article"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.data.get("added"))

    def test_rate_article_updates_rating(self):
        url = reverse("rate-content")
        resp = self.client.post(
            url, {"content_type": "article", "content_id": self.article.pk, "rating": 5}, format="json"
        )
        self.assertEqual(resp.status_code, 200)
        self.article.refresh_from_db()
        self.assertEqual(self.article.rating_count, 1)
        self.assertAlmostEqual(self.article.average_rating, 5.0)
