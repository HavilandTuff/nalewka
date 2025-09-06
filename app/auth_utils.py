import datetime
from functools import wraps
from typing import Callable, Optional

import jwt
from flask import current_app, jsonify, request

from app import db
from app.models import User


def encode_auth_token(user_id: int) -> Optional[str]:
    """
    Generates the Auth Token
    :param user_id: User ID
    :return: token string
    """
    try:
        payload = {
            "exp": datetime.datetime.utcnow()
            + datetime.timedelta(days=1),  # Token expires in 1 day
            "iat": datetime.datetime.utcnow(),
            "sub": str(user_id),  # Convert to string as required by JWT
        }
        return jwt.encode(
            payload, current_app.config.get("SECRET_KEY"), algorithm="HS256"
        )
    except Exception:
        return None


def decode_auth_token(auth_token: str) -> Optional[int]:
    """
    Decodes the auth token
    :param auth_token: Authentication token
    :return: user ID or None
    """
    try:
        payload = jwt.decode(
            auth_token, current_app.config.get("SECRET_KEY"), algorithms=["HS256"]
        )
        return int(payload["sub"])  # Convert back to integer
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f: Callable) -> Callable:
    """
    Decorator for requiring token authentication
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            try:
                token = auth_header.split(" ")[1]  # Expecting "Bearer <token>"
            except IndexError:
                return jsonify({"message": "Bearer token malformed"}), 401
        if not token:
            return jsonify({"message": "Token is missing"}), 401

        user_id = decode_auth_token(token)
        if not user_id:
            return jsonify({"message": "Token is invalid or expired"}), 401

        current_user = db.session.get(User, user_id)
        if not current_user:
            return jsonify({"message": "User not found"}), 401

        # Add current_user to kwargs so it can be accessed in the route
        kwargs["current_user"] = current_user
        return f(*args, **kwargs)

    return decorated
