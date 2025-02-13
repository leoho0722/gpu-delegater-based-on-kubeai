class UnsupportedModelError(Exception):

    def __init__(self, error: str, **kwargs):
        """Unsupported model Exception.

        Args:
            error (`str`): Error message
            kwargs (`Dict[str, Any]`): Original error message
        """

        self.error = error
        self.kwargs = kwargs
