import asyncio
import json
from logging import Logger
from typing import Dict, List, Optional

from apis import InferenceRequest
from config import parse_config, ServerConfig
from exceptions import InvalidRequestError, InferenceError, UnsupportedModelError
from gpu.dispatcher import GPUDispatcher
from k8s.kubeai import apply_kubeai_model_custom_resource, KubeAIModelException
from llm.models import OllamaBuiltinModel
from llm.openai import auth_signin, generate_openai_api_key, chat_completions


class LLMService:

    # ==================== Properties ====================

    _server_config: ServerConfig = None

    _gpu_dispatcher: GPUDispatcher = None

    _openai_api_key: str = None

    # ==================== Initialization ====================

    def __init__(self, logger: Logger):
        """Initialize the LLM Service.

        Args:
            logger (`Logger`): The logger object.
        """

        if not self._server_config:
            self._server_config = parse_config()

        self.logger = logger

        if not self._gpu_dispatcher:
            self._gpu_dispatcher = GPUDispatcher(
                logger=logger,
                ollama_parameters_worker_url=self._server_config.ollama_parameters_worker_url
            )

        if not self._openai_api_key:
            self._openai_api_key = asyncio.run(self._get_openai_api_key())

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

        Raises: `LLMInferenceError`: If the inference fails.
        """

        # 3-1: Get KubeAI model Custom Resource YAML

        model = OllamaBuiltinModel(request.model)
        self.logger.info(f"Model Name: {model.value}")
        self.logger.info(f"Model YAML:\n{json.dumps(model.yaml, indent=4)}")

        # 3-2. Get Available GPU resources (e.g., NVIDIA GPU)

        available_gpus = await self._gpu_dispatcher.get_available_gpus(model.value)
        if available_gpus is None or len(available_gpus.gpu_nodes) < 1:
            self.logger.error("No available GPU resources")
            raise InferenceError("No available GPU resources", 500)
        
        self.logger.debug(
            f"Available GPUs:\n{available_gpus.model_dump_json(indent=4)}"
        )

        # 3-2-1. Get the resource profile of the available GPU resources

        resourceProfile = self._gpu_dispatcher.convert_to_kubeai_gpu_resources_name(
            selected_gpu=available_gpus.gpu_nodes[0]
        )
        self.logger.info(f"Selected resource profile: {resourceProfile}")

        # 3-2-2. Set the resource profile of the available GPU resources to the KubeAI model Custom Resource YAML

        patch_model_yaml = model.yaml
        patch_model_yaml["spec"]["resourceProfile"] = resourceProfile

        # 3-3. Patch KubeAI model Custom Resource to Kubernetes Cluster

        try:
            apply_kubeai_model_custom_resource(patch_model_yaml)
        except KubeAIModelException as e:
            raise InferenceError(e.error, 500)

        # 3-4. Send a request to the KubeAI API server to inference using the created model

        async for chunk in chat_completions(
            model=patch_model_yaml["metadata"]["name"],
            system_prompt=request.system_prompt,
            user_prompt=request.user_prompt,
            api_key=self._openai_api_key,
            base_url=self._server_config.base_url,
        ):
            yield chunk.content

    # ==================== Private Methods ====================

    def _validate_model(self, model: str):
        """Validate the model name.

        Args:
            model (`str`): The model name.

        Raises: 
            UnsupportedModelException: If the model is unsupported.
        """

        import yaml

        SUPPORTED_MODEL_FILEPATH = "supported-model.yaml"

        with open(SUPPORTED_MODEL_FILEPATH, "r") as f:
            supported_models: Dict[str, List[str]] = yaml.safe_load(f)
            f.close()

        if model not in supported_models["models"]:
            raise UnsupportedModelError(f"Model {model} is not supported.")

    async def _get_openai_api_key(self):
        """Get the OpenAI API key.

        Returns:
            api_key (`str`): The OpenAI API key.
        """

        token: Optional[str] = await auth_signin(self._server_config)
        if token is None:
            raise RuntimeError("Failed to sign in")

        api_key: Optional[str] = await generate_openai_api_key(self._server_config, token)
        if api_key is None:
            api_key = token

        return api_key
