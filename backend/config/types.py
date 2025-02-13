from typing import Any, Dict

from pydantic import BaseModel


class ServerConfig(BaseModel):

    version: str

    host: str

    port: int

    base_url: str

    webui_url: str

    timeout: float

    user: Dict[str, str]

    ollama_parameters_worker_url: str

    concurrent: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ServerConfig":
        return ServerConfig(**data)
