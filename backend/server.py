from fastapi import FastAPI

from config import parse_config, ServerConfig
from controllers import InferenceController, RootController, VersionController
from routes.endpoints import Endpoints
from services.llm import LLMService
from utils.logger import KubeAIGPUDelegateLogger

app = FastAPI()

logger = KubeAIGPUDelegateLogger()

# InferenceController
llm_service = LLMService(logger.getLogger())
inference_controller = InferenceController(llm_service)

# RootController
root_controller = RootController()

# VersionController
version_controller = VersionController()

# Register Routers
app.include_router(inference_controller.router,
                   prefix=f"{Endpoints.PATH_PREFIX.path}/llm")
app.include_router(root_controller.router)
app.include_router(version_controller.router,
                   prefix=Endpoints.PATH_PREFIX.path)

if __name__ == "__main__":
    config: ServerConfig = parse_config()
    print(f"Server Config:\n{config.model_dump_json(indent=4)}")

    import uvicorn
    uvicorn.run(app, host=config.host, port=config.port)
