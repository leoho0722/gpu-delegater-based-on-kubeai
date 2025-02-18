from typing import Any, Dict, List

import httpx

from exceptions.network import NetworkError


class NetworkService:

    # ==================== Properties ====================

    _aclient: httpx.AsyncClient = None

    # ==================== Constructor ====================

    def __init__(self, timeout: float):
        self._aclient = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout, read=timeout)
        )

    # ==================== Public Methods ====================

    async def post(
        self,
        url: str,
        body: Dict[str, Any],
        additional_headers: List[Dict[str, str]],
    ) -> Dict[str, Any]:

        headers = self._set_headers(additional_headers)

        try:
            response = await self._aclient.post(
                url=url,
                json=body,
                headers=headers,
            )

            if response.status_code == 200:
                resp_body = response.json()
                return resp_body
            else:
                raise response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"HTTP Status Error: {e.response}")
            raise NetworkError(
                "HTTP Status Error", e.response.status_code)
        except httpx.RequestError as e:
            print(f"Request Error: {e.request}")
            raise NetworkError("Request Error", 400)
        except httpx.RemoteProtocolError as e:
            print(f"Remote Protocol Error: {e.request}")
            raise NetworkError("Remote Protocol Error", 500)
        except Exception as e:
            print(f"Unknown Error: {e}")
            raise NetworkError("Unknown Error", 500)

    # ==================== Private Methods ====================

    def _get_default_headers(self) -> Dict[str, str]:
        """Get the default headers for the HTTP client.

        Returns:
            default_headers (`Dict[str, str]`): The default headers for the HTTP client.
        """

        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        return default_headers

    def _set_headers(self, new: List[Dict[str, str]]) -> Dict[str, str]:
        """Set the headers for the HTTP client.

        Args:
            new (`List[Dict[str, str]]`): The new headers to be set.

        Returns:
            headers (`Dict[str, str]`): The headers for the HTTP client.
        """

        headers = self._get_default_headers()

        for h in new:
            headers.update(h)

        return headers
