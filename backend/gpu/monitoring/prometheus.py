import asyncio
from typing import Dict, List

import httpx


class PrometheusClient:
    """Prometheus client to interact with the Prometheus server."""

    _url: str = None
    _timeout: float = None
    _aclient: httpx.AsyncClient = None

    def __init__(self, url: str, timeout: float = 60.0):
        """Initializes the Prometheus client to interact with the Prometheus server.

        Args:
            url (`str`): URL of the Prometheus server.
            timeout (`float`): Timeout for the HTTP requests.
        """

        self.url = url
        self.timeout = timeout

    @property
    def url(self):
        """URL of the Prometheus server."""

        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    @property
    def timeout(self):
        """Timeout for the HTTP requests."""

        return self._timeout

    @timeout.setter
    def timeout(self, value):
        self._timeout = value
        self._htimeout = httpx.Timeout(value)
        self._aclient = httpx.AsyncClient(timeout=self._htimeout)

    async def get_targets(self):
        """Get all of the targets that Prometheus is scraping.

        Returns:
            targets (`Dict`): Targets that Prometheus is scraping.
        """

        response = await self._aclient.get(f"{self.url}/api/v1/targets")
        response.raise_for_status()

        return response.json()

    async def execute_query(self, query):
        """Execute a query on the Prometheus server.

        Args:
            query (`str`): PromQL query to execute

        Returns:
            response (`Dict`): Query result from the Prometheus server
        """

        response = await self._aclient.get(f"{self.url}/api/v1/query", params={"query": query})
        response.raise_for_status()

        return response.json()

    async def execute_multiple_queries(self, queries: List[str]) -> Dict[str, Dict]:
        """Execute multiple queries on the Prometheus server.

        Args:
            queries (`List[str]`): List of PromQL queries to execute

        Returns:
            queries_response (`Dict[str, Dict]`): Dictionary of query results from the Prometheus server
        """

        queries_response: Dict[str, Dict] = {}

        futures = await asyncio.gather(*[self.execute_query(query) for query in queries])

        for i, query in enumerate(queries):
            queries_response[query] = futures[i]

        return queries_response
