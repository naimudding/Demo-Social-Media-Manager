from typing import Dict

class ResponseHandler:
    """
        Default class to handle Error responses
    """
    @staticmethod
    def handle_error_response(resp, message="error") -> Dict:
        return {"message": "error", "data": resp}

    @staticmethod
    def handle_internal_error() -> Dict:
        return {"message": "Internal Server Error", "data": dict()}