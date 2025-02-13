from typing import Any, Dict

from pydantic import BaseModel


class ServerConfig(BaseModel):

    version: str

    host: str

    port: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ServerConfig":
        return ServerConfig(**data)
