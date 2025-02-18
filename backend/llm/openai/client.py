from typing import Optional

from langchain_openai.chat_models import ChatOpenAI


class OpenAIClient:

    # ==================== Properties ====================

    _base_url: str
    """OpenAI API Server base URL"""

    _api_key: str
    """OpenAI API key"""

    _timeout: float
    """Timeout for requests to OpenAI completion API."""

    # ==================== Constructor ====================

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 600.0
    ):
        """Initialize the OpenAI API Client.

        Args:
            base_url (`str`): OpenAI API Server base URL
            api_key (`str`): OpenAI API key
            timeout (`float`): Timeout for requests to OpenAI completion API, default is `600.0`
        """

        self._base_url = base_url
        self._api_key = api_key
        self._timeout = timeout

    # ==================== Public Methods ====================

    async def chat_completions(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.0,
    ):
        """Chat with OpenAI API

        Args:
            model (`str`): model name
            system_prompt (`str`): System Prompt for the model
            user_prompt (`str`): User Prompt for the model
            max_tokens (`Optional[int]`): Maximum tokens to generate, default is `None`
            temperature (`float`): Sampling temperature, default is `0.0`
        """

        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=self._timeout,
            api_key=self._api_key,
            base_url=self._base_url,
        )

        messages = [
            ("system", system_prompt),
            ("human", user_prompt),
        ]

        for chunk in llm.stream(messages):
            yield chunk
