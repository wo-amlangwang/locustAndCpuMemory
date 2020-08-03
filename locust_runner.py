import gevent
import os
from Users.root_user import RootUser
from locust import User
from locust.env import Environment
from locust.stats import stats_writer


class LocustRunner:

    def __init__(self, base_url: str, user: User = RootUser):
        self.env = Environment(user_classes=[user])
        self.env.host = base_url
        self.env.create_local_runner()

    def start_web_ui(self):
        self.env.create_web_ui("127.0.0.1", 8089)

    def stop_web_ui(self):
        self.env.web_ui.stop()

    def run(self, user_count: int, hatch_rate: int, total_run_time: int, csv_prefix: str):
        self.env.runner.start(user_count, hatch_rate)
        gevent.spawn(stats_writer, self.env, csv_prefix, False)
        gevent.spawn_later(total_run_time, lambda: self.env.runner.quit())

    def wait_runner(self):
        self.env.runner.greenlet.join()


if __name__ == '__main__':
    lr = LocustRunner("http://localhost:9000")
    lr.start_web_ui()
    lr.run(1, 1, 60, os.path.dirname(os.path.realpath(__file__)) + "/log")
    lr.wait_runner()
