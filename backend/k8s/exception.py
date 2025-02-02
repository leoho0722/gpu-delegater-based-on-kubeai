class KubernetesPodException(Exception):

    def __init__(self, error: str, **kwargs):
        """Kubernetes Pod Exception

        Args:
            error (str): Error message
            kwargs (Dict[str, Any]): Original error message
        """

        super().__init__(self.error, self.kwargs)

        self.error = error
        self.kwargs = kwargs
