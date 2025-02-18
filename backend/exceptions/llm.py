class UnsupportedModelError(Exception):

    def __init__(self, error: str, **kwargs):
        """Unsupported model Exception.

        Args:
            error (`str`): Error message
            kwargs (`Dict[str, Any]`): Original error message
        """

        self.error = error
        """Error message"""

        self.kwargs = kwargs
        """Original error message"""


class UnsupportedLLMRuntimeError(Exception):

    def __init__(self, error: str, **kwargs):
        """Unsupported LLM runtime Exception.

        Args:
            error (`str`): Error message
            kwargs (`Dict[str, Any]`): Original error message
        """

        self.error = error
        """Error message"""

        self.kwargs = kwargs
        """Original error message"""
