class KubeAIModelError(Exception):

    def __init__(self, error: str, **kwargs):
        """KubeAI Model Exception

        Args:
            error (`str`): Error message
            kwargs (`Dict[str, Any]`): Original error message
        """

        self.error = error
        """Error message"""

        self.kwargs = kwargs
        """Original error message"""


class KubeAIOllamaModelPodError(Exception):

    def __init__(self, error: str, **kwargs):
        """KubeAI Ollama Model Pod Exception

        Args:
            error (`str`): Error message
            kwargs (`Dict[str, Any]`): Original error message
        """

        self.error = error
        """Error message"""

        self.kwargs = kwargs
        """Original error message"""
