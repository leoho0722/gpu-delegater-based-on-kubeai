from ollama import AsyncClient


class OllamaClient:

    _aclient: AsyncClient = None

    def __init__(self, host: str):
        self._aclient = AsyncClient(host)

    async def list(self):
        """List Ollama Models

        Returns:
            models (`ListResponse`): List of Ollama Models
        """

        return await self._aclient.list()
