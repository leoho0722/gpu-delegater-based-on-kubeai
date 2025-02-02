from typing import Any, Dict, List

import yaml

from backend.gpu.dispatcher.types import GPUModel, GPUModelList


def parse_gpu_models(file_path: str = "backend/gpu/dispatcher/gpu_models.yaml") -> GPUModelList:
    """Parse GPU models from YAML file

    Args:
        file_path (str): GPU models YAML file path

    Returns:
        parsed_gpu_models (`GPUModelList`): Parsed GPU models
    """

    with open(file_path, "r") as f:
        gpu_models: List[Dict[str, Any]] = yaml.safe_load(f)
        f.close()

    parsed_gpu_models = GPUModelList(
        gpu_models=[
            GPUModel(
                model=str(gpu["model"]),
                vram=int(gpu["vram"])
            ) for gpu in gpu_models
        ]
    )

    return parsed_gpu_models
