from typing import Optional
from ._types import BaseRequest, BaseResponse


class InferenceRequest(BaseRequest):

    model: str
    """LLM model name"""

    temperature: float = 0.0

    max_tokens: Optional[int] = None


class InferenceResponse(BaseResponse):

    chunk: str = ""
