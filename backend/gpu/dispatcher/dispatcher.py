import math
import re
from logging import Logger
from typing import Dict, List

from .parser import parse_gpu_models
from .types import (
    GPU,
    GPUModelList,
    GPUNode,
    GPUNodeList,
    ParsedModelDetails
)
from gpu.monitoring.prometheus import PrometheusClient
from llm.ollama import OllamaClient, ModelDetails
from utils.constants.format import iB


class GPUDispatcher:

    _instance = None

    def __new__(cls, *args, **kwargs):
        '''
        GPU Dispatcher Singleton Instance
        '''

        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    _node_gpu_info: Dict[str, Dict] = {}
    """Raw Node GPU Information from Prometheus"""

    _gpu_node_list: GPUNodeList = None
    """List of Kubernetes GPU Node Information"""

    _gpu_model_list: GPUModelList = None
    """List of GPU Models"""

    _prometheus_client: PrometheusClient = None
    """Prometheus Client to interact with Prometheus Server"""

    _ollama_client: OllamaClient = None
    """Ollama Client to interact with Ollama Parameters Worker"""

    def __init__(
        self,
        logger: Logger,
        ollama_parameters_worker_url: str,
        prometheus_server_port: int = 30090,
        prometheus_client_timeout: float = 60.0
    ):
        '''Initializes the GPU Dispatcher to dispatch the GPU resources.

        Args:
            logger (`Logger`): Logger
            ollama_parameters_worker_url (`str`): Ollama Parameters Worker URL
            prometheus_server_port (`int`): Prometheus Server Port. Default is `30090`
            prometheus_client_timeout (`float`): Prometheus Client Timeout. Default is `60.0`
        '''

        self.logger = logger

        self._prometheus_client = PrometheusClient(
            url=f"http://0.0.0.0:{prometheus_server_port}",
            timeout=prometheus_client_timeout
        )

        self._ollama_client = OllamaClient(ollama_parameters_worker_url)

    # ============================== Properties ==============================

    @property
    def node_gpu_info(self):
        """Raw Node GPU Information from Prometheus"""

        return self._node_gpu_info

    @node_gpu_info.setter
    def node_gpu_info(self, value: Dict[str, Dict]):
        self._node_gpu_info = value

    @property
    def gpu_node_list(self):
        """List of Kubernetes GPU Node Information"""

        return self._gpu_node_list

    @gpu_node_list.setter
    def gpu_node_list(self, value: GPUNodeList):
        self._gpu_node_list = value

    # ============================== Public Methods ==============================

    async def get_available_gpus(self, model_name: str, runtime: str) -> GPUNodeList:
        gpu_node_list = await self._get_gpu_node_list()

        available_gpus: GPUNodeList = None
        estimate_vram = await self._calc_model_estimate_vram(model_name, runtime)

        for gpu_node in gpu_node_list.gpu_nodes:
            # 依照 VRAM 大小排序 GPU (從小到大)
            sorted_gpus = sorted(gpu_node.gpus, key=lambda x: x.free_memory)
            total_node_vram = sum(gpu.free_memory for gpu in gpu_node.gpus)

            self.logger.info(
                f"Node: {gpu_node.node_name}, Total VRAM: {total_node_vram}, Required VRAM: {estimate_vram}"
            )

            # 如果無法估算 LLM 模型所需的 GPU VRAM，則不進行 GPU 選擇
            if not estimate_vram:
                self.logger.warning("Cannot estimate the required VRAM")
                break

            # 檢查節點總 VRAM 是否足夠
            if total_node_vram >= estimate_vram:
                required_gpus = []
                current_vram = 0

                # 從 VRAM 較小的 GPU 開始選擇
                for gpu in sorted_gpus:
                    required_gpus.append(gpu)
                    current_vram += gpu.free_memory

                    if current_vram >= estimate_vram:
                        # 找到足夠的 GPU 組合
                        existing_node = GPUNode(
                            node_name=gpu_node.node_name,
                            gpus=[]
                        )
                        existing_node.gpus.extend(required_gpus)

                        if available_gpus is None:
                            available_gpus = GPUNodeList()

                        available_gpus.gpu_nodes.append(existing_node)

                        self.logger.info(
                            f"Node {gpu_node.node_name}: Selected {len(available_gpus.gpu_nodes[0].gpus)} GPU(s)"
                        )

                        break

        return available_gpus

    # async def get_available_gpus(
    #     self,
    #     model_name: str,
    #     ollama_models: ListResponse,
    #     use_multiple_gpus: bool = False
    # ) -> GPUNodeList:
    #     """Get the available GPUs based on the free memory and the estimated VRAM.

    #     Args:
    #         model_name (`str`): Model name for LLM inference
    #         ollama_models (`ListResponse`): Ollama Models
    #         use_multiple_gpus (`bool`): Use multiple GPUs or not. Default is `False` (use single GPU)

    #     Returns:
    #         available_gpus (`GPUNodeList`): Available GPUs
    #     """

    #     gpu_node_list = await self._get_gpu_node_list()

    #     available_gpus: GPUNodeList = GPUNodeList()

    #     # 估算 LLM 推理所需的 VRAM 大小
    #     estimate_vram = self._calc_inference_estimate_vram(
    #         model_name, ollama_models
    #     )

    #     for gpu_node in gpu_node_list.gpu_nodes:
    #         print(
    #             f"Node: {gpu_node.node_name}, GPU Count: {len(gpu_node.gpus)}"
    #         )
    #         if len(gpu_node.gpus) > 1:
    #             if use_multiple_gpus:
    #                 # 使用多張 GPU 進行推理，要計算該節點上所有 GPU 的總 VRAM

    #                 total_vram = sum(
    #                     [gpu.free_memory for gpu in gpu_node.gpus]
    #                 )

    #                 self._filter_available_gpus(
    #                     total_vram, estimate_vram, available_gpus, gpu_node.node_name, gpu_node.gpus
    #                 )
    #             else:
    #                 for gpu in gpu_node.gpus:
    #                     self._filter_available_gpus(
    #                         gpu.free_memory, estimate_vram, available_gpus, gpu_node.node_name, gpu_node.gpus
    #                     )
    #         else:
    #             for gpu in gpu_node.gpus:
    #                 self._filter_available_gpus(
    #                     gpu.free_memory, estimate_vram, available_gpus, gpu_node.node_name, gpu_node.gpus
    #                 )

    #     return available_gpus

    def convert_to_kubeai_gpu_resources_name(self, selected_gpu: GPUNode) -> str:
        """Convert the selected GPU resources to the KubeAI GPU resources name.

        Args:
            selected_gpu (`GPUNode`): Selected GPU resources

        Returns:
            kubeai_gpu_resources_name (`str`): KubeAI GPU resources name
        """

        selected_gpu_model = selected_gpu.gpus[-1].name
        selected_gpu_count = len(selected_gpu.gpus)
        self.logger.info(
            f"Selected GPU Model: {selected_gpu_model}, Count: {selected_gpu_count}"
        )

        # GPU Model Mapping 表
        if self._gpu_model_list is None:
            self._gpu_model_list = parse_gpu_models()

        model_number = None
        vram = None

        for gpu in self._gpu_model_list.gpu_models:
            if gpu.model == selected_gpu_model:
                model_number = selected_gpu_model.split("RTX")[1].strip()
                model_number = model_number.replace(" ", "").lower()
                vram = gpu.vram
                break

        if not model_number or not vram:
            raise ValueError(f"Unsupported GPU model: {selected_gpu_model}")

        kubeai_gpu_resources_name = f"nvidia-gpu-{model_number}-{vram}gb:{selected_gpu_count}"

        return kubeai_gpu_resources_name

    # ============================== Private Methods ==============================

    async def _get_gpu_metrics_from_prometheus(self):
        """Get GPU metrics from Prometheus.

        Returns:
            gpu_metrics (`Dict[str, Dict]`): GPU metrics
        """

        queries = [
            "DCGM_FI_DEV_FB_FREE",
            "DCGM_FI_DEV_FB_USED",
            "DCGM_FI_DEV_GPU_TEMP",
            "DCGM_FI_DEV_GPU_UTIL",
            "DCGM_FI_DEV_POWER_USAGE"
        ]

        node_gpu_info = await self._prometheus_client.execute_multiple_queries(queries)

        self.node_gpu_info = node_gpu_info

    def _prometheus_metrics_name_mapping(self, metrics_name: str) -> str:
        """Mapping Prometheus metrics name to the GPU metrics name.

        Args:
            metrics_name (`str`): Prometheus metrics name

        Returns:
            gpu_metrics_name (`str`): GPU metrics name
        """

        match metrics_name:
            case "DCGM_FI_DEV_FB_FREE": return "free_memory"
            case "DCGM_FI_DEV_FB_USED": return "used_memory"
            case "DCGM_FI_DEV_GPU_TEMP": return "temperature"
            case "DCGM_FI_DEV_GPU_UTIL": return "memory_usage"
            case "DCGM_FI_DEV_POWER_USAGE": return "power_usage"

    async def _get_gpu_node_list(self) -> GPUNodeList:
        """Get the List of Kubernetes GPU Node Information.

        Returns:
            gpu_node_list (`GPUNodeList`): List of Kubernetes GPU Node Information
        """

        # Get GPU metrics from Prometheus
        await self._get_gpu_metrics_from_prometheus()

        gpu_node_list: GPUNodeList = GPUNodeList()

        for query, response in self.node_gpu_info.items():
            for node in response["data"]["result"]:
                node_name = node["metric"]["kubernetes_node"]
                value = node["value"][1]

                existing_node = next(
                    (
                        node for node in gpu_node_list.gpu_nodes if node.node_name == node_name
                    ), None
                )
                if existing_node:
                    gpu_node = existing_node
                else:
                    gpu_node = GPUNode(node_name=node_name, gpus=[])
                    gpu_node_list.gpu_nodes.append(gpu_node)

                gpu_index = node["metric"]["gpu"]
                gpu_uuid = node["metric"]["UUID"]
                gpu_name = node["metric"]["modelName"]

                gpu_info = next(
                    (
                        gpu for gpu in gpu_node.gpus if gpu.index == f"cuda:{gpu_index}"
                    ), None
                )

                if not gpu_info:
                    gpu_info = GPU(
                        index=f"cuda:{gpu_index}",
                        uuid=gpu_uuid,
                        name=gpu_name,
                        free_memory=0,
                        used_memory=0,
                        temperature=0,
                        memory_usage=0,
                        power_usage=0
                    )

                    gpu_node.gpus.append(gpu_info)

                for gpu_info in gpu_node.gpus:
                    if gpu_info.index == f"cuda:{gpu_index}":
                        gpu_info.__setattr__(
                            self._prometheus_metrics_name_mapping(query),
                            int(float(value))
                        )

        self._gpu_node_list = gpu_node_list

        return gpu_node_list

    def _filter_available_gpus(
        self,
        free_memory: int,
        estimate_vram: int,
        available_gpus: GPUNodeList,
        node: str,
        gpus: List[GPU]
    ):
        """Filter the available GPUs based on the free memory and the estimated VRAM.

        Args:
            free_memory (`int`): Free memory of the GPU.
            estimate_vram (`int`): Estimated VRAM required for the LLM inference.
            available_gpus (`GPUNodeList`): List to store the available GPUs.
            node (`str`): Kubernetes Node name.
            gpus (`List[GPUInfo]`): List of GPUs information.
        """
        print(f"Free Memory: {free_memory}, Estimate VRAM: {estimate_vram}")
        if free_memory > estimate_vram:
            existing_node = next(
                (gpu_node for gpu_node in available_gpus.gpu_nodes if gpu_node.node_name == node), None
            )

            if not existing_node:
                existing_node = GPUNode(node_name=node, gpus=[])
                available_gpus.gpu_nodes.append(existing_node)

            existing_node.gpus = gpus

    async def _calc_model_estimate_vram(self, model_name: str, runtime: str) -> int:
        '''
        根據模型的 `參數量` 與 `量化等級` 計算進行 LLM 推理所需的預估 GPU 記憶體

        Args:
            model_name (`str`): 要進行 LLM Inference 的模型名稱
            runtime (`str`): LLM Runtime

        Returns:
            estimate_vram (`int`): 預估 GPU 記憶體 (MiB)
        '''

        def parse_model_details(model_details: ModelDetails) -> ParsedModelDetails:
            '''
            解析模型參數量與量化等級

            Args:
                model_details (`ModelDetails`): 模型詳細資訊

            Returns:
                parsed_model_details (`ParsedModelDetails`): 解析後的模型資訊
            '''

            match = re.match(
                r"(\d+(\.\d+)?)([KMB])",
                model_details.parameter_size
            )
            if not match:
                raise ValueError("Invalid format")
            parameter_size = float(match.group(1))

            match = re.search(r'\d+', model_details.quantization_level)
            if not match:
                raise ValueError("No number found in the string")
            quantization_level = int(match.group(0))

            parsed_model_details = ParsedModelDetails(
                parameter_size=parameter_size,
                quantization_level=quantization_level
            )

            return parsed_model_details

        def calc_estimate_vram(parsed_model_details: ParsedModelDetails) -> int:
            '''
            計算進行 LLM 推理所需的預估 GPU 記憶體

            Args:
                parsed_model_details (`ParsedModelDetails`): 解析後的模型資訊

            Returns:
                estimate_vram (`int`): 預估 GPU 記憶體 (MiB)
            '''

            # 計算公式參考：https://www.substratus.ai/blog/calculating-gpu-memory-for-llm
            # `result = ((parameter_size * 4 / (32 / quantization_level)) * 1.2) * iB`
            # `result` 為估計的 VRAM 使用量 (MiB)
            # `parameter_size` 為模型參數量 (B)
            # `quantization_level` 為模型量化等級
            # `iB` 為 1024，用來將 GiB 轉換成 MiB
            # `1.2` 多計算 20% 的 GPU 記憶體，避免記憶體不足

            parameter_size = parsed_model_details.parameter_size
            quantization_level = parsed_model_details.quantization_level

            estimate_vram = math.ceil(
                ((parameter_size * 4 / (32 / quantization_level)) * 1.2) * iB
            )

            return estimate_vram

        match runtime:
            case "ollama":
                ollama_models = await self._ollama_client.list()
                self.logger.info(
                    f"Ollama Models:\n{ollama_models.model_dump_json(indent=4)}"
                )

                for model in ollama_models.models:
                    if model.model == model_name:
                        parsed_model_details = parse_model_details(
                            model.details)

                        estimate_vram = calc_estimate_vram(
                            parsed_model_details)

                        self.logger.info(
                            f"Model: {model_name}, Estimate VRAM: {estimate_vram} MiB"
                        )

                        return estimate_vram
            case "vllm":
                pass
