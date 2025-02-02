import json
from typing import Dict

from pydantic import BaseModel


class Config(BaseModel):

    webui_url: str

    base_url: str

    timeout: float = 60.0

    user: Dict[str, str]

    ollama_parameters_worker_url: str

    concurrent: int = 1

    @classmethod
    def from_dict(cls, config: Dict) -> 'Config':
        webui_url = config.get('webui_url', "http://10.20.1.93:32000/api/v1")
        base_url = config.get('base_url', "http://10.20.1.93:32000/openai")
        timeout = config.get('timeout', 60.0)
        user = config.get('user', {"email": "", "password": ""})
        ollama_parameters_worker_url = config.get(
            'ollama_parameters_worker_url',
            "http://10.20.1.93:31434"
        )
        concurrent = config.get('concurrent', 1)

        return cls(
            webui_url=webui_url,
            base_url=base_url,
            timeout=timeout,
            user=user,
            ollama_parameters_worker_url=ollama_parameters_worker_url,
            concurrent=concurrent
        )

    def json(self, use_load: bool = False):
        if use_load:
            return json.loads(self.model_dump_json(indent=4))
        else:
            return self.model_dump_json(indent=4)
