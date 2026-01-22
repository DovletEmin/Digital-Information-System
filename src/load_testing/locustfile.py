from locust import HttpUser, between, task
import os
import random


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.token = None
        username = os.getenv("LOCUST_USERNAME")
        password = os.getenv("LOCUST_PASSWORD")
        if username and password:
            try:
                resp = self.client.post(
                    "/auth/login/", json={"username": username, "password": password}
                )
                if resp.status_code in (200, 201):
                    data = resp.json()
                    # support both TokenObtainPair and custom responses
                    token = (
                        data.get("access")
                        or data.get("token")
                        or data.get("access_token")
                    )
                    if token:
                        self.token = token
                        self.client.headers.update(
                            {"Authorization": f"Bearer {self.token}"}
                        )
            except Exception:
                pass

    # High traffic: main pages and API list

    @task(2)
    def api_list_dissertation_categories(self):
        self.client.get("/api/dissertation-categories/")

    @task(2)
    def api_list_article_categories(self):
        self.client.get("/api/article-categories/")

    @task(2)
    def api_list_book_categories(self):
        self.client.get("/api/book-categories/")

    @task(2)
    def api_list_article_categories_id(self):
        category_id = random.randint(1, 2)
        self.client.get(f"/api/article-categories/{category_id}/")

    @task(2)
    def api_list_book_categories_id(self):
        category_id = random.randint(1, 2)
        self.client.get(f"/api/book-categories/{category_id}/")

    @task(2)
    def api_list_dissertation_categories_id(self):
        category_id = random.randint(1, 2)
        self.client.get(f"/api/dissertation-categories/{category_id}/")

    @task(4)
    def api_list_books(self):
        self.client.get("/api/books/")

    @task(3)
    def api_list_articles(self):
        self.client.get("/api/articles/")

    @task(2)
    def api_list_dissertations(self):
        self.client.get("/api/dissertations/")

    # Details and related actions
    @task(2)
    def book_detail(self):
        book_id = random.randint(1, 2)
        self.client.get(f"/api/books/{book_id}/")

    @task(2)
    def article_detail(self):
        article_id = random.randint(1, 2)
        self.client.get(f"/api/articles/{article_id}/")

    @task(2)
    def dissertation_detail(self):
        dissertation_id = random.randint(1, 2)
        self.client.get(f"/api/dissertations/{dissertation_id}/")

    @task(1)
    def search(self):
        q = random.choice(["article", "book", "dissertation"])
        self.client.get(f"/search/?content_type={q}")
