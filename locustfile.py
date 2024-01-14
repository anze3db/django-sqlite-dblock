from locust import HttpUser, task


class HelloWorldUser(HttpUser):
    @task
    def fetch_index_and_bail(self):
        self.client.get("create_user/")
