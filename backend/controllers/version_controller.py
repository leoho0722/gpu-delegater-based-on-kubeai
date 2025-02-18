from fastapi import APIRouter
from fastapi.responses import JSONResponse

from apis.version import VersionResponse
from config import parse_config, ServerConfig
from routes.endpoints import Endpoints


class VersionController:

    def __init__(self):
        self.router = APIRouter()
        self.setup_routes()

    def setup_routes(self):
        @self.router.get(Endpoints.VERSION.path, response_model=VersionResponse)
        async def version():
            config: ServerConfig = parse_config()

            response = VersionResponse(
                status="ok",
                code=200,
                message=f"GPU Delegater based on KubeAI version {config.version}!",
            )
            response_json = response.json(pretty=True)

            return JSONResponse(response_json, status_code=response.code)
