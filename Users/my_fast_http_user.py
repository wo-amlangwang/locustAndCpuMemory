import logging
import time
from locust.contrib.fasthttp import FastHttpUser, FastHttpSession
from locust.env import Environment

logger = logging.getLogger(__name__)


class MyFastHttpUser(FastHttpUser):

    def __init__(self, environment):
        super().__init__(environment)

        self.client = MyFastHttpSession(
            self.environment,
            base_url=self.host,
            network_timeout=self.network_timeout,
            connection_timeout=self.connection_timeout,
            max_redirects=self.max_redirects,
            max_retries=self.max_retries,
            insecure=self.insecure,
        )


class MyFastHttpSession(FastHttpSession):

    def __init__(self, environment: Environment, base_url: str, insecure=True, **kwargs):
        super().__init__(environment, base_url, insecure, **kwargs)

    def get(self, path, headers, **kwargs):
        """Sends a GET request"""
        start = time.time()
        response = super().request("GET", path, headers=headers, **kwargs)
        end = time.time()
        try:
            response.raise_for_status()
        except:
            logger.info(str(response.status_code) + ":" + str(end - start) + ":" + path + ":" + str(headers))
        return response
