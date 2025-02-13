from typing import Any, Dict

import yaml

from .types import ServerConfig

CONFIG_FILEPATH = "backend/config/config.yaml"


def parse_config() -> ServerConfig:
    with open(CONFIG_FILEPATH, "r") as f:
        config_yaml: Dict[str, Any] = yaml.safe_load(f)
        f.close()

        config = ServerConfig(**config_yaml)

        return config
