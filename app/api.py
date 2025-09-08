from typing import Any

from flask import Blueprint, jsonify, request

from app import db
from app.auth_utils import encode_auth_token, token_required
from app.models import User
from app.services import (
    create_api_key,
    create_batch,
    create_batch_with_ingredients,
    create_ingredient,
    create_liquor,
    delete_api_key,
    delete_batch,
    delete_ingredient,
    delete_liquor,
    get_all_ingredients,
    get_api_keys_for_user,
    get_batch_by_id,
    get_batches_for_liquor,
    get_ingredient_by_id,
    get_liquor_by_id,
    get_liquors_for_user,
    update_batch,
    update_batch_bottles,
    update_ingredient,
    update_liquor,
)

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


@api_v1_bp.route("/auth/api-keys", methods=["POST"])
@token_required
def create_api_key_endpoint(current_user: User) -> Any:
    """Create a new API key for the current user"""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name")
    if not name:
        return jsonify({"error": "Name is required"}), 400

    api_key, error = create_api_key(current_user.id, name)
    if error:
        return jsonify({"error": error}), 500

    return (
        jsonify(
            {
                "id": api_key.id,
                "name": api_key.name,
                "key": api_key.key,
                "created_at": api_key.created_at.isoformat(),
                "is_active": api_key.is_active,
            }
        ),
        201,
    )


@api_v1_bp.route("/auth/api-keys", methods=["GET"])
@token_required
def list_api_keys(current_user: User) -> Any:
    """List all API keys for the current user"""
    api_keys = get_api_keys_for_user(current_user.id)

    return (
        jsonify(
            [
                {
                    "id": api_key.id,
                    "name": api_key.name,
                    "created_at": api_key.created_at.isoformat(),
                    "last_used": (
                        api_key.last_used.isoformat() if api_key.last_used else None
                    ),
                    "is_active": api_key.is_active,
                }
                for api_key in api_keys
            ]
        ),
        200,
    )


@api_v1_bp.route("/auth/api-keys/<int:api_key_id>", methods=["DELETE"])
@token_required
def delete_api_key_endpoint(current_user: User, api_key_id: int) -> Any:
    """Delete an API key"""
    success, error = delete_api_key(api_key_id, current_user.id)
    if error:
        return jsonify({"error": error}), 404 if "not found" in error.lower() else 500

    return jsonify({"message": "API key deleted successfully"}), 200


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


@api_v1_bp.route("/liquors", methods=["GET"])
@token_required
def get_liquors(current_user: User) -> Any:
    """List all liquors for the current user"""
    liquors = get_liquors_for_user(current_user.id)
    return (
        jsonify(
            [
                {
                    "id": liquor.id,
                    "name": liquor.name,
                    "description": liquor.description,
                    "created_at": liquor.created.isoformat(),
                }
                for liquor in liquors
            ]
        ),
        200,
    )


@api_v1_bp.route("/liquors", methods=["POST"])
@token_required
def create_liquor_endpoint(current_user: User) -> Any:
    """Create a new liquor"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name")
    if not name:
        return jsonify({"error": "Name is required"}), 400

    description = data.get("description")

    liquor = create_liquor(user_id=current_user.id, name=name, description=description)

    return (
        jsonify(
            {
                "id": liquor.id,
                "name": liquor.name,
                "description": liquor.description,
                "created_at": liquor.created.isoformat(),
            }
        ),
        201,
    )


@api_v1_bp.route("/liquors/<int:liquor_id>", methods=["GET"])
@token_required
def get_liquor(current_user: User, liquor_id: int) -> Any:
    """Get details of a specific liquor"""
    liquor = get_liquor_by_id(liquor_id, current_user.id)
    if not liquor:
        return jsonify({"error": "Liquor not found"}), 404

    return (
        jsonify(
            {
                "id": liquor.id,
                "name": liquor.name,
                "description": liquor.description,
                "created_at": liquor.created.isoformat(),
            }
        ),
        200,
    )


@api_v1_bp.route("/liquors/<int:liquor_id>", methods=["PUT"])
@token_required
def update_liquor_endpoint(current_user: User, liquor_id: int) -> Any:
    """Update a specific liquor"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    liquor = update_liquor(liquor_id, current_user.id, data)

    if not liquor:
        return jsonify({"error": "Liquor not found"}), 404

    return (
        jsonify(
            {
                "id": liquor.id,
                "name": liquor.name,
                "description": liquor.description,
                "created_at": liquor.created.isoformat(),
            }
        ),
        200,
    )


@api_v1_bp.route("/liquors/<int:liquor_id>", methods=["DELETE"])
@token_required
def delete_liquor_endpoint(current_user: User, liquor_id: int) -> Any:
    """Delete a specific liquor"""
    success = delete_liquor(liquor_id, current_user.id)
    if not success:
        return jsonify({"error": "Liquor not found"}), 404

    return jsonify({}), 204


@api_v1_bp.route("/ingredients", methods=["GET"])
def get_ingredients() -> Any:
    """List all ingredients"""
    ingredients = get_all_ingredients()
    return (
        jsonify(
            [
                {
                    "id": ingredient.id,
                    "name": ingredient.name,
                    "description": ingredient.description,
                    "created_at": ingredient.created_at.isoformat(),
                }
                for ingredient in ingredients
            ]
        ),
        200,
    )


@api_v1_bp.route("/ingredients", methods=["POST"])
@token_required
def create_ingredient_endpoint(current_user: User) -> Any:
    """Create a new ingredient"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name = data.get("name")
    if not name:
        return jsonify({"error": "Name is required"}), 400

    # Check if ingredient with this name already exists
    existing_ingredient = get_all_ingredients()
    for ingredient in existing_ingredient:
        if ingredient.name.lower() == name.lower():
            return jsonify({"error": "Ingredient with this name already exists"}), 400

    description = data.get("description")

    ingredient = create_ingredient(name=name, description=description)

    return (
        jsonify(
            {
                "id": ingredient.id,
                "name": ingredient.name,
                "description": ingredient.description,
                "created_at": ingredient.created_at.isoformat(),
            }
        ),
        201,
    )


@api_v1_bp.route("/ingredients/<int:ingredient_id>", methods=["GET"])
def get_ingredient(ingredient_id: int) -> Any:
    """Get details of a specific ingredient"""
    ingredient = get_ingredient_by_id(ingredient_id)
    if not ingredient:
        return jsonify({"error": "Ingredient not found"}), 404

    return (
        jsonify(
            {
                "id": ingredient.id,
                "name": ingredient.name,
                "description": ingredient.description,
                "created_at": ingredient.created_at.isoformat(),
            }
        ),
        200,
    )


@api_v1_bp.route("/ingredients/<int:ingredient_id>", methods=["PUT"])
@token_required
def update_ingredient_endpoint(current_user: User, ingredient_id: int) -> Any:
    """Update a specific ingredient"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    ingredient = update_ingredient(ingredient_id, data)

    if not ingredient:
        return jsonify({"error": "Ingredient not found"}), 404

    return (
        jsonify(
            {
                "id": ingredient.id,
                "name": ingredient.name,
                "description": ingredient.description,
                "created_at": ingredient.created_at.isoformat(),
            }
        ),
        200,
    )


@api_v1_bp.route("/ingredients/<int:ingredient_id>", methods=["DELETE"])
@token_required
def delete_ingredient_endpoint(current_user: User, ingredient_id: int) -> Any:
    """Delete a specific ingredient"""
    success = delete_ingredient(ingredient_id)
    if not success:
        return jsonify({"error": "Ingredient not found"}), 404

    return jsonify({}), 204


@api_v1_bp.route("/liquors/<int:liquor_id>/batches", methods=["GET"])
@token_required
def get_batches(current_user: User, liquor_id: int) -> Any:
    """List all batches for a liquor"""
    # First check if the liquor exists and belongs to the user
    liquor = get_liquor_by_id(liquor_id, current_user.id)
    if not liquor:
        return jsonify({"error": "Liquor not found"}), 404

    batches = get_batches_for_liquor(liquor_id)
    return (
        jsonify(
            [
                {
                    "id": batch.id,
                    "date": batch.date.isoformat(),
                    "description": batch.description,
                    "bottle_count": batch.bottle_count,
                    "bottle_volume": batch.bottle_volume,
                    "bottle_volume_unit": batch.bottle_volume_unit,
                    "total_volume": batch.total_volume,
                    "ingredient_count": batch.ingredient_count,
                }
                for batch in batches
            ]
        ),
        200,
    )


@api_v1_bp.route("/liquors/<int:liquor_id>/batches", methods=["POST"])
@token_required
def create_batch_endpoint(current_user: User, liquor_id: int) -> Any:
    """Create a new batch"""
    # First check if the liquor exists and belongs to the user
    liquor = get_liquor_by_id(liquor_id, current_user.id)
    if not liquor:
        return jsonify({"error": "Liquor not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Prepare batch data
    batch_data = {
        "liquor_id": liquor_id,
        "description": data.get("description", ""),
        "bottle_count": data.get("bottle_count"),
        "bottle_volume": data.get("bottle_volume"),
        "bottle_volume_unit": data.get("bottle_volume_unit", "ml"),
    }

    # Handle date if provided
    if "date" in data:
        try:
            # Parse the date string and convert to datetime
            from datetime import datetime

            date_str = data["date"]
            if isinstance(date_str, str):
                # Try to parse as date first, then as datetime
                try:
                    from datetime import date

                    parsed_date = date.fromisoformat(date_str)
                    batch_data["date"] = datetime.combine(
                        parsed_date, datetime.min.time()
                    )
                except ValueError:
                    batch_data["date"] = datetime.fromisoformat(date_str)
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400

    # If ingredients are provided, use the create_batch_with_ingredients service
    if "ingredients" in data:
        batch, error = create_batch_with_ingredients(data, liquor_id, current_user.id)
    else:
        # Otherwise, create a simple batch
        batch, error = create_batch(batch_data)

    if error:
        return jsonify({"error": error}), 400

    return (
        jsonify(
            {
                "id": batch.id,
                "date": batch.date.isoformat(),
                "description": batch.description,
                "bottle_count": batch.bottle_count,
                "bottle_volume": batch.bottle_volume,
                "bottle_volume_unit": batch.bottle_volume_unit,
                "total_volume": batch.total_volume,
                "ingredient_count": batch.ingredient_count,
            }
        ),
        201,
    )


@api_v1_bp.route("/batches/<int:batch_id>", methods=["GET"])
@token_required
def get_batch(current_user: User, batch_id: int) -> Any:
    """Get details of a specific batch"""
    batch = get_batch_by_id(batch_id)
    if not batch:
        return jsonify({"error": "Batch not found"}), 404

    # Check if the batch belongs to a liquor that belongs to the user
    liquor = get_liquor_by_id(batch.liquor_id, current_user.id)
    if not liquor:
        return jsonify({"error": "Batch not found"}), 404

    # Include formulas data in the response
    formulas_data = []
    for formula in batch.formulas:
        formulas_data.append(
            {
                "id": formula.id,
                "ingredient_id": formula.ingredient_id,
                "ingredient_name": formula.ingredient.name,
                "quantity": formula.quantity,
                "unit": formula.unit,
            }
        )

    return (
        jsonify(
            {
                "id": batch.id,
                "date": batch.date.isoformat(),
                "description": batch.description,
                "bottle_count": batch.bottle_count,
                "bottle_volume": batch.bottle_volume,
                "bottle_volume_unit": batch.bottle_volume_unit,
                "total_volume": batch.total_volume,
                "ingredient_count": batch.ingredient_count,
                "formulas": formulas_data,
            }
        ),
        200,
    )


@api_v1_bp.route("/batches/<int:batch_id>", methods=["PUT"])
@token_required
def update_batch_endpoint(current_user: User, batch_id: int) -> Any:
    """Update a specific batch"""
    batch = get_batch_by_id(batch_id)
    if not batch:
        return jsonify({"error": "Batch not found"}), 404

    # Check if the batch belongs to a liquor that belongs to the user
    liquor = get_liquor_by_id(batch.liquor_id, current_user.id)
    if not liquor:
        return jsonify({"error": "Batch not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Remove liquor_id from data if present, as it shouldn't be updated
    data.pop("liquor_id", None)

    updated_batch = update_batch(batch_id, data)
    if not updated_batch:
        return jsonify({"error": "Batch not found"}), 404

    return (
        jsonify(
            {
                "id": updated_batch.id,
                "date": updated_batch.date.isoformat(),
                "description": updated_batch.description,
                "bottle_count": updated_batch.bottle_count,
                "bottle_volume": updated_batch.bottle_volume,
                "bottle_volume_unit": updated_batch.bottle_volume_unit,
                "total_volume": updated_batch.total_volume,
                "ingredient_count": updated_batch.ingredient_count,
            }
        ),
        200,
    )


@api_v1_bp.route("/batches/<int:batch_id>", methods=["DELETE"])
@token_required
def delete_batch_endpoint(current_user: User, batch_id: int) -> Any:
    """Delete a specific batch"""
    batch = get_batch_by_id(batch_id)
    if not batch:
        return jsonify({"error": "Batch not found"}), 404

    # Check if the batch belongs to a liquor that belongs to the user
    liquor = get_liquor_by_id(batch.liquor_id, current_user.id)
    if not liquor:
        return jsonify({"error": "Batch not found"}), 404

    success = delete_batch(batch_id)
    if not success:
        return jsonify({"error": "Batch not found"}), 404

    return jsonify({}), 204


@api_v1_bp.route("/batches/<int:batch_id>/bottles", methods=["PUT"])
@token_required
def update_batch_bottles_endpoint(current_user: User, batch_id: int) -> Any:
    """Update bottle information for a batch"""
    batch = get_batch_by_id(batch_id)
    if not batch:
        return jsonify({"error": "Batch not found"}), 404

    # Check if the batch belongs to a liquor that belongs to the user
    liquor = get_liquor_by_id(batch.liquor_id, current_user.id)
    if not liquor:
        return jsonify({"error": "Batch not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Prepare data for the service function
    form_data = {
        "bottle_count": data.get("bottle_count"),
        "bottle_volume": data.get("bottle_volume"),
        "bottle_volume_unit": data.get("bottle_volume_unit", "ml"),
    }

    updated_batch, error = update_batch_bottles(batch_id, current_user.id, form_data)
    if error:
        return jsonify({"error": error}), 400

    return (
        jsonify(
            {
                "id": updated_batch.id,
                "date": updated_batch.date.isoformat(),
                "description": updated_batch.description,
                "bottle_count": updated_batch.bottle_count,
                "bottle_volume": updated_batch.bottle_volume,
                "bottle_volume_unit": updated_batch.bottle_volume_unit,
                "total_volume": updated_batch.total_volume,
                "ingredient_count": updated_batch.ingredient_count,
            }
        ),
        200,
    )
