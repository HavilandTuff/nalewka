from typing import Any

from flask import Blueprint, jsonify, request

from app import db
from app.auth_utils import encode_auth_token, token_required
from app.models import User

# Create a Blueprint object for API endpoints
api_bp = Blueprint("api", __name__, url_prefix="/api")

# API version 1 blueprint
api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/v1")

# Register the v1 blueprint with the main api blueprint
api_bp.register_blueprint(api_v1_bp)


@api_v1_bp.route("/")
def api_root() -> Any:
    """API root endpoint"""
    return jsonify(
        {
            "message": "Welcome to the Nalewka API",
            "version": "1.0",
            "documentation": "/api/docs",  # Placeholder for future documentation
        }
    )


@api_v1_bp.route("/auth/login", methods=["POST"])
def api_login() -> Any:
    """API login endpoint to generate auth token"""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = db.session.execute(
        db.select(User).filter_by(username=username)
    ).scalar_one_or_none()

    if user is None or not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401

    # Generate auth token
    auth_token = encode_auth_token(user.id)
    if not auth_token:
        return jsonify({"error": "Failed to generate auth token"}), 500

    return (
        jsonify(
            {
                "message": "Successfully logged in",
                "auth_token": auth_token,
                "user_id": user.id,
            }
        ),
        200,
    )


@api_v1_bp.route("/users/me", methods=["GET"])
@token_required
def get_current_user(current_user: User) -> Any:
    """Get current user profile"""
    return jsonify(
        {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "created_at": current_user.created_at.isoformat(),
        }
    )


@api_v1_bp.route("/users/me", methods=["PUT"])
@token_required
def update_current_user(current_user: User) -> Any:
    """Update current user profile"""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Update user fields if provided
    if "username" in data:
        # Check if username is already taken
        existing_user = db.session.execute(
            db.select(User).filter_by(username=data["username"])
        ).scalar_one_or_none()

        if existing_user and existing_user.id != current_user.id:
            return jsonify({"error": "Username already taken"}), 400

        current_user.username = data["username"]

    if "email" in data:
        # Check if email is already taken
        existing_user = db.session.execute(
            db.select(User).filter_by(email=data["email"])
        ).scalar_one_or_none()

        if existing_user and existing_user.id != current_user.id:
            return jsonify({"error": "Email already taken"}), 400

        current_user.email = data["email"]

    try:
        db.session.commit()
        return (
            jsonify(
                {
                    "id": current_user.id,
                    "username": current_user.username,
                    "email": current_user.email,
                    "message": "User updated successfully",
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update user: {str(e)}"}), 500
