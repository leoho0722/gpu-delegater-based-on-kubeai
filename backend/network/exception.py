class NetworkException(Exception):

    def __init__(self, error: str, status_code: int, **kwargs):
        """Network Exception

        Args:
            error (str): Error message
            status_code (int): HTTP status code
            kwargs (Dict[str, Any]): Original error message
        """

        super().__init__(self.error, self.status_code, self.kwargs)

        self.error = error
        self.status_code = status_code
        self.kwargs = kwargs
