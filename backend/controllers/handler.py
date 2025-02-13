from fastapi.responses import JSONResponse, RedirectResponse

from apis import (
    InferenceRequest, InferenceResponse,
    VersionResponse
)
from config import parse_config, ServerConfig
from ._app import app
from exceptions import InvalidRequestError, InferenceError
from routes import Endpoints
from services.llm import LLMService
from utils.logger import KubeAIGPUDelegateLogger

logger = KubeAIGPUDelegateLogger()
llm_service = LLMService(logger=logger.getLogger())


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
        try:
            async for chunk in llm_service.inference(request):
                response = InferenceResponse(
                    status="ok",
                    code=200,
                    chunk=chunk,
                )
                response_json = response.json(pretty=True)

                return JSONResponse(response_json, status_code=response.code)
        except InferenceError as e:
            response = InferenceResponse(
                status="failed",
                code=e.status_code,
                error_message=e.error,
            )
            response_json = response.json(pretty=True)

            return JSONResponse(response_json, status_code=response.code)
