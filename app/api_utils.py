from typing import Any, Dict, Optional, Tuple


def success_response(
    data: Any = None, message: Optional[str] = None, status_code: int = 200
) -> Tuple[Dict[str, Any], int]:
    """Create a consistent success response"""
    response = {}
    if data is not None:
        response.update(data)
    if message:
        response["message"] = message
    return response, status_code


def error_response(
    message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None
) -> Tuple[Dict[str, Any], int]:
    """Create a consistent error response"""
    response = {"error": message}
    if details:
        response["details"] = details
    return response, status_code


def paginated_response(
    data: list, page: int, per_page: int, total: int, message: Optional[str] = None
) -> Tuple[Dict[str, Any], int]:
    """Create a paginated response"""
    response = {
        "data": data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page,
        },
    }
    if message:
        response["message"] = message
    return response, 200
