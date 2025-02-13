import json
from logging import Logger
from typing import Dict, List

from api import InferenceRequest
from llm.models import OllamaBuiltinModel
from service.exception import InvalidRequestError, UnsupportedModelError


class LLMService:

    # ==================== Initialization ====================

    def __init__(self, logger: Logger):
        """Initialize the LLM Service.

        Args:
            logger (`Logger`): The logger object.
        """

        self.logger = logger

    # ==================== Public Methods ====================

    def validate(self, request: InferenceRequest):
        """Validate the request.

        Args:
            request (`InferenceRequest`): The request object.

        Raises:
            RequestException: If the request is invalid.
        """

        try:
            self._validate_model(request.model)
        except UnsupportedModelError as e:
            raise InvalidRequestError(e.error, 400, ** e.kwargs)

    async def inference(self, request: InferenceRequest):
        """Run LLM Streaming Inference via GPU Delegater in Kubernetes.

        Args:
            request (`InferenceRequest`): The request object.

        Returns:
            chunk (`str`): The streaming inference result.
        """

        # 3-1: Get KubeAI model Custom Resource YAML

        model = OllamaBuiltinModel(request.model)
        self.logger.info(f"Model Name: {model.value}")
        self.logger.info(f"Model YAML:\n{json.dumps(model.yaml, indent=4)}")

        return "test"

    # ==================== Private Methods ====================

    def _validate_model(self, model: str):
        """Validate the model name.

        Args:
            model (`str`): The model name.

        Raises: 
            UnsupportedModelException: If the model is unsupported.
        """

        import yaml

        SUPPORTED_MODEL_FILEPATH = "backend/supported-model.yaml"

        with open(SUPPORTED_MODEL_FILEPATH, "r") as f:
            supported_models: Dict[str, List[str]] = yaml.safe_load(f)
            f.close()

        if model not in supported_models["models"]:
            raise UnsupportedModelError(f"Model {model} is not supported.")
