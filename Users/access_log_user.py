from locust.contrib.fasthttp import FastHttpUser
from Utils.parser import parse
from Utils.util import get_slash
import os


class AccessLogUser(FastHttpUser):
    min_wait = 100
    max_wait = 120
    tasks = parse(os.path.abspath(f'.{get_slash()}access.log'))
