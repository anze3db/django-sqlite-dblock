from locust import HttpUser, task


class HelloWorldUser(HttpUser):
    @task
    def fetch_read(self):
        self.client.get("read/")

    @task
    def fetch_read_transaction(self):
        self.client.get("read_transaction/")

    @task
    def fetch_write(self):
        self.client.post("write/")

    @task
    def fetch_read_write(self):
        self.client.post("read_write/")

    @task
    def fetch_write_read(self):
        self.client.post("write_read/")

    @task
    def fetch_read_write_transaction(self):
        self.client.post("read_write_transaction/")

    @task
    def fetch_write_read_transaction(self):
        self.client.post("write_read_transaction/")

    @task
    def fetch_read_write_transaction_immediate(self):
        self.client.post("read_write_transaction_immediate/")
