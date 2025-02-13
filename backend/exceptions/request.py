class InvalidRequestError(Exception):

    def __init__(
        self,
        error: str,
        status_code: int = 400,
        **kwargs
    ):
        """Invalid request Exception.

        Args:
            error (`str`): Error message
            status_code (`int`): Status code
            kwargs (`Dict[str, Any]`): Original error message
        """

        self.error = error
        self.status_code = status_code
        self.kwargs = kwargs
