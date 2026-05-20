from locust import HttpUser, task, between
import random

class DjangoUser(HttpUser):
    wait_time = between(0.5, 2)
    host = "http://127.0.0.1:8000"

    # GET эндпоинты

    @task(3)
    def get_posts(self):
        self.client.get("/api/posts/")

    @task(2)
    def get_post_detail(self):
        post_id = random.randint(1, 10)
        self.client.get(f"/api/posts/{post_id}/")

    @task(2)
    def get_users(self):
        self.client.get("/api/users/")

    @task(2)
    def get_user_detail(self):
        user_id = random.randint(60, 71)
        self.client.get(f"/api/users/{user_id}/")

    @task(1)
    def get_posts_by_category(self):
        slugs = ["technology", "science", "art", "sports", "music"]
        slug = random.choice(slugs)
        self.client.get(f"/api/category/{slug}/")

    @task(1)
    def get_user_posts(self):
        username = f"user{random.randint(60, 71)}"
        self.client.get(f"/api/user/{username}/posts/")

    # POST эндпоинты
    @task(1)
    def register_user(self):
        random_suffix = random.randint(1, 100000)
        data = {
            "username": f"newuser_{random_suffix}",
            "password": "NewUser123!",
            "email": f"user_{random_suffix}@test.com"
        }
        self.client.post("/api/register/", json=data)