from Utils.singleton import get_access_log
from locust.contrib.fasthttp import FastHttpUser
from Utils.parser import parse


class AccessLogUser(FastHttpUser):
    min_wait = 100
    max_wait = 120

    def __init__(self, environment):
        super().__init__(environment)
        access_log = get_access_log()
        self.tasks = parse(access_log)
