from locust import task, between
from locust.contrib.fasthttp import FastHttpUser


class RootUser(FastHttpUser):
    wait_time = between(1, 1)

    @task
    def root_task(self):
        self.client.get("/")