class NetworkError(Exception):

    def __init__(self, error: str, status_code: int, **kwargs):
        """Network Exception

        Args:
            error (`str`): Error message
            status_code (`int`): HTTP status code
            kwargs (`Dict[str, Any]`): Original error message
        """

        self.error = error
        """Error message"""

        self.status_code = status_code
        """HTTP status code"""

        self.kwargs = kwargs
        """Original error message"""
