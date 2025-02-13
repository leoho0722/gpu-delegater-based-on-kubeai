from typing import Any, Dict, Literal

from pydantic import BaseModel


class BaseRequest(BaseModel):
    """Base request model"""

    def dict(self):
        """Convert model to Dict object

        Returns:
            Converted model dict object
        """

        return self.model_dump()

    def json(self, pretty=False):
        """Convert model to JSON Serializable object

        Args:
            pretty (`bool`, Optional): Pretty print JSON. Defaults to False.

        Returns:
            Converted model JSON Serializable object if pretty is True, else `Dict[str, Any]`
        """

        if pretty:
            import json

            return json.loads(self.model_dump_json(indent=4))

        return self.model_dump_json(indent=4)


class BaseResponse(BaseModel):
    """Base response model"""

    status: str = Literal["ok", "failed"]
    """Response status"""

    code: int = 200
    """Response code"""

    error_message: str = ""
    """Error message"""

    def dict(self):
        """Convert model to Dict object

        Returns:
            Converted model dict object
        """

        return self.model_dump()

    def json(self, pretty=False) -> (Dict[str, Any] | str):
        """Convert model to JSON Serializable object

        Args:
            pretty (`bool`, Optional): Pretty print JSON. Defaults to False.

        Returns:
            Converted model JSON Serializable object if pretty is True, else `Dict[str, Any]`
        """

        if pretty:
            import json

            return json.loads(self.model_dump_json(indent=4))

        return self.model_dump_json(indent=4)
