import asyncio
import json
from logging import Logger
from typing import Any, Dict, List, Optional

from .network import NetworkService
from apis import InferenceRequest
from config import parse_config, ServerConfig
from exceptions import (
    InferenceError,
    UnsupportedLLMRuntimeError,
    UnsupportedModelError,
    InvalidRequestError,
    NetworkError
)
from gpu.dispatcher import GPUDispatcher
from k8s.kubeai import apply_kubeai_model_custom_resource, KubeAIModelError
from llm.models import OllamaBuiltinModel
from llm.openai import OpenAIClient


class LLMService:

    # ==================== Properties ====================

    _server_config: ServerConfig = None

    _network_service: NetworkService = None

    _gpu_dispatcher: GPUDispatcher = None

    _openai_api_key: str = None

    _openai_client: OpenAIClient = None

    # ==================== Constructor ====================

    def __init__(self, logger: Logger):
        """Initialize the LLM Service.

        Args:
            logger (`Logger`): The logger object.
        """

        if not self._server_config:
            self._server_config = parse_config()

        if not self._network_service:
            self._network_service = NetworkService(
                timeout=self._server_config.timeout
            )

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

        try:
            self._validate_runtime(request.runtime)
        except UnsupportedLLMRuntimeError as e:
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

        available_gpus = await self._gpu_dispatcher.get_available_gpus(model.value, request.runtime)
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
        except KubeAIModelError as e:
            raise InferenceError(e.error, 500)

        # 3-4. Send a request to the KubeAI API server to inference using the created model

        if not self._openai_client:
            self._openai_client = OpenAIClient(
                base_url=self._server_config.base_url,
                api_key=self._openai_api_key,
                timeout=self._server_config.timeout
            )

        async for chunk in self._openai_client.chat_completions(
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
            UnsupportedModelError: If the model is unsupported.
        """

        import yaml

        SUPPORTED_MODEL_FILEPATH = "supported-model.yaml"

        with open(SUPPORTED_MODEL_FILEPATH, "r") as f:
            supported_models: Dict[str, List[str]] = yaml.safe_load(f)
            f.close()

        if model not in supported_models["ollama"] or model not in supported_models["vllm"]:
            raise UnsupportedModelError(f"Model {model} is not supported.")

    def _validate_runtime(self, runtime: str):
        """Validate the LLM Runtime name.

        Args:
            runtime (`str`): The LLM Runtime name.

        Raises:
            UnsupportedLLMRuntimeError: If the LLM Runtime is unsupported.
        """

        if runtime.lower() not in ["ollama", "vllm"]:
            raise UnsupportedLLMRuntimeError(
                f"LLM Runtime {runtime} is not supported."
            )

    async def _get_openai_api_key(self):
        """Get the OpenAI API key.

        Returns:
            api_key (`str`): The OpenAI API key.
        """

        token: Optional[str] = await self._auth_signin()
        if token is None:
            raise RuntimeError("Failed to sign in")

        api_key: Optional[str] = await self._generate_openai_api_key(token)
        if api_key is None:
            api_key = token

        return api_key

    async def _auth_signin(self) -> Optional[str]:
        """Sign in to Open WebUI.

        Returns:
            token (`Optional[str]`): The generated Open WebUI token.
        """

        try:
            response: Dict[str, Any] = await self._network_service.post(
                url=f"{self._server_config.webui_url}/auths/signin",
                json={
                    "email": self._server_config.user.get("email"),
                    "password": self._server_config.user.get("password"),
                },
            )
            return response.get("token")
        except NetworkError as e:
            print(f"Failed to sign in, Error: {e}")
            return None

    async def _generate_openai_api_key(self, token: str) -> Optional[str]:
        """Generate OpenAI API Key.

        Args:
            token (`str`): The Open WebUI token.

        Returns:
            api_key (`Optional[str]`): The generated OpenAI API key.
        """

        try:
            response: Dict[str, Any] = await self._network_service.post(
                url=f"{self._server_config.webui_url}/auths/api_key",
                json={},
                additional_headers=[
                    {"Authorization": f"Bearer {token}"}
                ],
            )
            return response.get("api_key")
        except NetworkError as e:
            print(f"Failed to generate OpenAI API Key, Error: {e}")
            return None
