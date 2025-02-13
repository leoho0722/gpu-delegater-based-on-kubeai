from enum import Enum


class Endpoints(Enum):

    ROOT = "/"

    VERSION = "/version"

    INFERENCE = "/inference"

    @property
    def path(self):
        return self.value
