from typing import Any, Dict, List

import yaml

from gpu.dispatcher.types import GPUModel, GPUModelList

GPU_MODEL_FILE_PATH = "gpu/dispatcher/gpu_models.yaml"


def parse_gpu_models() -> GPUModelList:
    """Parse GPU models from YAML file

    Args:
        file_path (str): GPU models YAML file path

    Returns:
        parsed_gpu_models (`GPUModelList`): Parsed GPU models
    """

    with open(GPU_MODEL_FILE_PATH, "r") as f:
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
