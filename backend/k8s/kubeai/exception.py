class KubeAIModelException(Exception):

    def __init__(self, error: str, **kwargs):
        """KubeAI Model Exception

        Args:
            error (str): Error message
            kwargs (Dict[str, Any]): Original error message
        """

        super().__init__(self.error, self.kwargs)

        self.error = error
        self.kwargs = kwargs


class KubeAIOllamaModelPodException(Exception):

    def __init__(self, error: str, **kwargs):
        """KubeAI Ollama Model Pod Exception

        Args:
            error (str): Error message
            kwargs (Dict[str, Any]): Original error message
        """

        super().__init__(self.error, self.kwargs)

        self.error = error
        self.kwargs = kwargs
