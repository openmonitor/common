import requests


class Callable():
    def __init__(
        self,
        callback: str
    ):
        self.callback = callback

    def call_by_get(self):
        return requests.get(self.callback)

    def call_by_post(self):
        return requests.post(self.callback)
