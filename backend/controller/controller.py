from fastapi.responses import JSONResponse, RedirectResponse

from api import (
    InferenceRequest, InferenceResponse,
    VersionResponse
)
from config import parse_config, ServerConfig
from controller._app import app
from route import Endpoints
from shared.utils.logger import KubeAIKubernetesClientLogger
from service import LLMService
from service.exception import InvalidRequestError

logger = KubeAIKubernetesClientLogger()
llm_service = LLMService()


@app.get(Endpoints.ROOT.path)
async def root():
    return RedirectResponse(Endpoints.VERSION.path)


@app.get(Endpoints.VERSION.path, response_model=VersionResponse)
async def version():
    config: ServerConfig = parse_config()

    response = VersionResponse(
        status="ok",
        code=200,
        message=f"GPU Delegater based on KubeAI version {config.version}!",
    )
    response_json = response.json(pretty=True)

    return JSONResponse(response_json, status_code=response.code)


@app.post(Endpoints.INFERENCE.path, response_model=InferenceResponse)
async def inference(request: InferenceRequest):
    try:
        llm_service.validate(request)
    except InvalidRequestError as e:
        response = InferenceResponse(
            status="failed",
            code=e.status_code,
            error_message=e.error,
        )
        response_json = response.json(pretty=True)

        return JSONResponse(response_json, status_code=response.code)
    else:
        response = InferenceResponse(
            status="ok",
            code=200,
            chunk="test",
        )
        response_json = response.json(pretty=True)

        return JSONResponse(response_json, status_code=response.code)
