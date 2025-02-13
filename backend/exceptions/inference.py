class InferenceError(Exception):

    def __init__(
        self,
        error: str,
        status_code: int = 500,
        **kwargs
    ):
        """LLM Inference Exception.

        Args:
            error (`str`): Error message
            status_code (`int`): Status code
            kwargs (`Dict[str, Any]`): Original error message
        """

        self.error = error
        """Error message"""

        self.status_code = status_code
        """Status code"""

        self.kwargs = kwargs
        """Original error message"""
