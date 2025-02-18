from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from ._base import BaseController
from routes.endpoints import Endpoints


class RootController(BaseController):

    def __init__(self):
        self.router = APIRouter()

        super().__init__()

    def setup_routes(self):
        @self.router.get(Endpoints.ROOT.path)
        async def root():
            return RedirectResponse(Endpoints.PATH_PREFIX.path + Endpoints.VERSION.path)
