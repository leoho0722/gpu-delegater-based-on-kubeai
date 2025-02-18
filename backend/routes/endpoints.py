from enum import Enum


class Endpoints(Enum):

    PATH_PREFIX = "/api"

    ROOT = "/"

    VERSION = "/version"

    INFERENCE = "/inference"

    @property
    def path(self):
        return self.value
