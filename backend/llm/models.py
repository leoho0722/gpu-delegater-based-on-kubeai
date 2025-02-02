from enum import Enum
from typing import Any, Dict, List

import yaml


def parse_model_yaml(model_yaml_file_path: str) -> Dict[str, Any]:
    """Parse the model YAML file

    Args:
        model_yaml_file_path (`str`): The model YAML file path

    Returns:
        parsed_model_yaml (`Dict[str, Any]`): The parsed model YAML
    """

    with open(model_yaml_file_path, 'r') as f:
        model_yaml: Dict[str, Any] = yaml.load(f, Loader=yaml.SafeLoader)
        return model_yaml


class OllamaBuiltinModel(Enum):
    """Ollama Builtin Model Enum"""

    Gemma2_2B = "gemma2:2b"
    """Gemma2 2B Ollama model (4bits quantized)"""

    Gemma2_9B = "gemma2:9b"
    """Gemma2 9B Ollama model (4bits quantized)"""

    Gemma2_27B = "gemma2:27b"
    """Gemma2 27B Ollama model (4bits quantized)"""

    Llama3_1_8B = "llama3.1:8b"
    """Llama3.1 8B Ollama model (4bits quantized)"""

    Llama3_2_3B = "llama3.2:3b"
    """Llama3.2 3B Ollama model (4bits quantized)"""

    Llama3_3_70B = "llama3.3:70b"
    """Llama3.3 70B Ollama model (4bits quantized)"""

    @property
    def yaml(self) -> Dict[str, str]:
        """Get the model YAML"""

        prefix_path = "backend/k8s/deploy/kubeai"

        match self.name:
            case "Gemma2_2B":
                return parse_model_yaml(f"{prefix_path}/gemma2-2b-builtin.yaml")
            case "Gemma2_9B":
                return parse_model_yaml(f"{prefix_path}/gemma2-9b-builtin.yaml")
            case "Gemma2_27B":
                return parse_model_yaml(f"{prefix_path}/gemma2-27b-builtin.yaml")
            case "Llama3_1_8B":
                return parse_model_yaml(f"{prefix_path}/llama3.1-8b-builtin.yaml")
            case "Llama3_2_3B":
                return parse_model_yaml(f"{prefix_path}/llama3.2-3b-builtin.yaml")
            case "Llama3_3_70B":
                return parse_model_yaml(f"{prefix_path}/llama3.3-70b-builtin.yaml")
            case _:
                raise ValueError(f"Invalid OllamaBuiltinModel")

    def allCases() -> List["OllamaBuiltinModel"]:
        """Get all cases of `OllamaBuiltinModel`"""

        return [
            OllamaBuiltinModel.Gemma2_2B,
            # OllamaBuiltinModel.Gemma2_9B,
            # OllamaBuiltinModel.Gemma2_27B,
            # OllamaBuiltinModel.Llama3_1_8B,
            # OllamaBuiltinModel.Llama3_2_3B,
            # OllamaBuiltinModel.Llama3_3_70B
        ]
