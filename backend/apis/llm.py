from typing import Optional
from ._types import BaseRequest, BaseResponse


class InferenceRequest(BaseRequest):

    model: str
    """LLM model name"""

    system_prompt: str

    user_prompt: str

    temperature: float = 0.0

    max_tokens: Optional[int] = None


class InferenceResponse(BaseResponse):

    chunk: str = ""
