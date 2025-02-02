from typing import List

from pydantic import BaseModel, Field


class GPU(BaseModel):

    index: str
    """GPU Index, Like `cuda:0`、`cuda:1`"""

    uuid: str
    """GPU UUID, Prefix start with `GPU-` if not enabled MIG instance else `MIG-`"""

    name: str
    """GPU model name, Like `NVIDIA GeForce RTX 4090`"""

    free_memory: int
    """GPU free memory, unit: MiB"""

    used_memory: int
    """GPU used memory, unit: MiB"""

    memory_usage: int
    """GPU memory usage"""

    temperature: int
    """GPU temperature, unit: Celsius"""

    power_usage: int
    """GPU power usage, unit: W"""


class GPUNode(BaseModel):

    node_name: str
    """Kubernetes Node name, Like `ubuntu-d830mt`、`ubuntu-ms-7d98`"""

    gpus: List[GPU]
    """All GPU information of the node"""


class GPUNodeList(BaseModel):

    gpu_nodes: List[GPUNode] = Field(default_factory=list)
    """GPU Node List"""


class ParsedModelDetails(BaseModel):

    parameter_size: float
    """LLM Parameter Size"""

    quantization_level: int
    """LLM Quantization Level"""


class GPUModel(BaseModel):

    model: str
    """GPU Model Name"""

    vram: int
    """GPU VRAM Size, unit: GiB"""


class GPUModelList(BaseModel):

    gpu_models: List[GPUModel] = Field(default_factory=list)
    """GPU Model List"""
