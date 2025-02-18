from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ._base import BaseController
from apis.llm import InferenceRequest, InferenceResponse
from exceptions.inference import InferenceError
from exceptions.request import InvalidRequestError
from routes.endpoints import Endpoints
from services.llm import LLMService


class InferenceController(BaseController):

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.router = APIRouter()

        super().__init__()

    def setup_routes(self):
        @self.router.post(Endpoints.INFERENCE.path, response_model=InferenceResponse)
        async def inference(request: InferenceRequest):
            try:
                self.llm_service.validate(request)
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
                    async for chunk in self.llm_service.inference(request):
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
