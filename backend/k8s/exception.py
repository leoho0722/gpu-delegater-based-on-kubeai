class KubernetesPodError(Exception):

    def __init__(self, error: str, **kwargs):
        """Kubernetes Pod Exception

        Args:
            error (`str`): Error message
            kwargs (`Dict[str, Any]`): Original error message
        """

        self.error = error
        """Error message"""

        self.kwargs = kwargs
        """Original error message"""
