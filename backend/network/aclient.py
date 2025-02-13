from typing import Any, Dict, List

import httpx

from .exception import NetworkException


def get_default_headers() -> Dict[str, str]:
    """Get the default headers for the HTTP client.

    Returns:
        default_headers (`Dict[str, str]`): The default headers for the HTTP client.
    """

    default_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    return default_headers


def set_headers(new: List[Dict[str, str]]) -> Dict[str, str]:
    """Set the headers for the HTTP client.

    Args:
        new (`List[Dict[str, str]]`): The new headers to be set.

    Returns:
        headers (`Dict[str, str]`): The headers for the HTTP client.
    """

    headers = get_default_headers()

    for h in new:
        headers.update(h)

    return headers


async def post(
    url: str,
    json: Dict,
    timeout: float,
    headers: Dict = get_default_headers(),
) -> Dict[str, Any]:
    """Make a POST request to the given URL.

    Args:
        url (`str`): The URL to make the POST request to.
        json (`Dict`): The JSON data to be sent in the POST request.
        timeout (`float`): The timeout for the request.
        headers (`Dict`): The headers for the request.

    Returns:
        resp_body (`Dict[str, Any]`): The response body of the POST request
    """

    h_timeout = httpx.Timeout(timeout, read=timeout)
    async with httpx.AsyncClient(timeout=h_timeout) as client:
        try:
            response = await client.post(
                url=url,
                json=json,
                headers=headers,
            )

            if response.status_code == 200:
                resp_body = response.json()
                return resp_body
            else:
                raise response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"HTTP Status Error: {e.response}")
            raise NetworkException("HTTP Status Error", e.response.status_code)
        except httpx.RequestError as e:
            print(f"Request Error: {e.request}")
            raise NetworkException("Request Error", 400)
        except httpx.RemoteProtocolError as e:
            print(f"Remote Protocol Error: {e.request}")
            raise NetworkException("Remote Protocol Error", 500)
        except Exception as e:
            print(f"Unknown Error: {e}")
            raise NetworkException("Unknown Error", 500)
