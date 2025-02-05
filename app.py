import argparse
import asyncio
import json
from logging import Logger

from backend.gpu.dispatcher.dispatcher import GPUDispatcher
from backend.k8s.kubeai import apply_kubeai_model_custom_resource
from backend.llm.models import OllamaBuiltinModel
from frontend.llm.auth import auth_signin, generate_openai_api_key
from frontend.llm.chat import chat_completions
from shared.config import parse_config, Config
from shared.utils.logger import KubeAIKubernetesClientLogger


async def run(
    logger: Logger,
    config: Config,
    system_prompt: str,
    user_prompt: str,
    model_name: str
):
    async def _run(
        system_prompt: str,
        user_prompt: str,
        api_key: str,
        base_url: str
    ):
        # 3-1: Get KubeAI model Custom Resource YAML

        model = OllamaBuiltinModel(model_name)
        logger.info(f"Model Name: {model.value}")
        logger.info(f"Model YAML:\n{json.dumps(model.yaml, indent=4)}")

        # 3-2. Get Available GPU resources (e.g., NVIDIA GPU)

        gpu_dispatcher = GPUDispatcher(
            logger=logger,
            ollama_parameters_worker_url=config.ollama_parameters_worker_url
        )
        available_gpus = await gpu_dispatcher.get_available_gpus(model.value)
        logger.debug(
            f"Available GPUs:\n{available_gpus.model_dump_json(indent=4)}"
        )

        if len(available_gpus.gpu_nodes) < 1:
            logger.error("No available GPU resources")
            return

        # 3-2-1. Get the resource profile of the available GPU resources

        resourceProfile = gpu_dispatcher.convert_to_kubeai_gpu_resources_name(
            selected_gpu=available_gpus.gpu_nodes[-1]
        )
        logger.info(f"Selected resource profile: {resourceProfile}")

        # 3-2-2. Set the resource profile of the available GPU resources to the KubeAI model Custom Resource YAML
        patch_model_yaml = model.yaml
        patch_model_yaml["spec"]["resourceProfile"] = resourceProfile

        # 3-3. Patch KubeAI model Custom Resource to Kubernetes Cluster
        apply_kubeai_model_custom_resource(patch_model_yaml)

        # 3-4. Send a request to the KubeAI API server to inference using the created model
        async for chunk in chat_completions(
            model=patch_model_yaml["metadata"]["name"],
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            api_key=api_key,
            base_url=base_url,
        ):
            print(chunk.content, end="")

    # 1. Get OpenAI API key
    token = await auth_signin(config)
    api_key = await generate_openai_api_key(config, token)
    if token is None:
        raise RuntimeError("Failed to sign in")
    if api_key is None:
        api_key = token

    # 2. Concurrently run the inference tasks
    tasks = [
        _run(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            api_key=api_key,
            base_url=config.base_url
        ) for _ in range(config.concurrent)
    ]

    await asyncio.gather(*tasks)


async def main(args: argparse.Namespace, config: Config):
    """Main function

    Args:
        args (`argparse.Namespace`): Parsed arguments
        config (`Config`): Parsed configuration file
    """

    # Get Logger instance
    logger = KubeAIKubernetesClientLogger()
    logger = logger.getLogger()

    # Running
    logger.info("Start Running...")

    system_prompt: str = args.system_prompt
    user_prompt: str = args.user_prompt
    model: str = args.model

    await run(logger, config, system_prompt, user_prompt, model)


def parsed_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--system_prompt",
        type=str,
        default="You are a helpful assistant that answers user questions. Please answer according to the user's question using Traditional Chinese.",
    )
    parser.add_argument(
        "--user_prompt",
        type=str,
        required=True
    )
    parser.add_argument(
        "-m", "--model",
        type=str,
        default="gemma2:9b",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parsed_args()

    # Parse configuration file
    parsed_config = parse_config()

    # Run main function
    asyncio.run(main(args, parsed_config))
