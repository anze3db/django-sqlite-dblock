from locust import HttpUser, task


# Output as dictionaries
def row_generator():
    counter = 0
    while True:
        yield dict(
            name=f"Name {counter}",
            campaign=f"Campaign {counter}",
            voice=f"Voice {counter}",
            recognize=f"Recognize {counter}",
            inside=counter,
            growth=f"Growth {counter}",
            side=counter,
            yard=f"Yard {counter}",
            discussion=f"Discussion {counter}",
        )
        counter += 1


rows = row_generator()
row = next(rows)


class HelloWorldUser(HttpUser):
    @task(10)
    def fetch_read(self):
        self.client.get("read/")

    @task(10)
    def fetch_read_transaction(self):
        self.client.get("read_transaction/")

    @task
    def fetch_write(self):
        self.client.post("write/", row)

    @task
    def fetch_read_write(self):
        self.client.post("read_write/", row)

    @task
    def fetch_write_read(self):
        self.client.post("write_read/", row)

    @task
    def fetch_read_write_transaction(self):
        self.client.post("read_write_transaction/", row)

    @task
    def fetch_write_read_transaction(self):
        self.client.post("write_read_transaction/", row)

    @task
    def fetch_read_write_transaction_immediate(self):
        self.client.post("read_write_transaction_immediate/", row)
