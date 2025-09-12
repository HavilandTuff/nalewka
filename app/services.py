import secrets
import string
from typing import Any, Dict, List, Optional, Tuple, Union

from app import db
from app.models import ApiKey, Batch, BatchFormula, Ingredient, Liquor
from app.repositories import (
    ApiKeyRepository,
    BatchFormulaRepository,
    BatchRepository,
    IngredientRepository,
    LiquorRepository,
)

liquor_repository = LiquorRepository()
batch_repository = BatchRepository()
api_key_repository = ApiKeyRepository()
ingredient_repository = IngredientRepository()
batch_formula_repository = BatchFormulaRepository()


def create_batch_with_ingredients(
    form_data: Dict[str, Any], liquor_id: int, user_id: int
) -> Tuple[Optional[Batch], Optional[str]]:
    """
    Service to create a batch and its ingredient formulas.
    Returns (batch_object, None) on success or (None, error_message) on failure.
    """
    liquor = liquor_repository.get(liquor_id)
    if not liquor or liquor.user_id != user_id:
        return None, "Liquor not found or access denied."

    try:
        bottle_volume_ml: float = form_data.get("bottle_volume") or 0
        if form_data.get("bottle_volume_unit") == "l" and bottle_volume_ml > 0:
            bottle_volume_ml *= 1000

        batch_data = {
            "description": form_data["batch_description"],
            "liquor_id": liquor_id,
            "bottle_count": form_data.get("bottle_count") or 0,
            "bottle_volume": bottle_volume_ml,
            "bottle_volume_unit": "ml",
        }

        formulas_data: List[Dict[str, Union[int, float, str]]] = []
        ingredients_data = form_data.get("ingredients", [])
        for ing_data in ingredients_data:
            if (
                ing_data.get("ingredient")
                and ing_data.get("quantity")
                and ing_data.get("unit")
            ):
                try:
                    quantity = float(ing_data["quantity"])
                    if quantity <= 0:
                        return (
                            None,
                            f"Ingredient quantity must be positive, got {quantity}",
                        )

                    formulas_data.append(
                        {
                            "ingredient_id": int(ing_data["ingredient"]),
                            "quantity": quantity,
                            "unit": str(ing_data["unit"]),
                        }
                    )
                except ValueError as e:
                    return None, f"Invalid ingredient data: {str(e)}"

        if not formulas_data:
            return None, "At least one valid ingredient must be added."

        return batch_repository.create_with_formulas(batch_data, formulas_data)
    except KeyError as e:
        return None, f"Missing required field: {str(e)}"
    except ValueError as e:
        return None, f"Invalid data format: {str(e)}"
    except Exception as e:
        return None, f"An unexpected error occurred: {str(e)}"


def update_batch_bottles(
    batch_id: int, user_id: int, form_data: Dict[str, Union[int, float]]
) -> Tuple[Optional[Batch], Optional[str]]:
    """
    Service to update the bottle information for a batch.
    Returns (batch_object, None) on success or (None, error_message) on failure.
    """
    batch = batch_repository.get(batch_id)
    if not batch:
        return None, "Batch not found."
    if batch.liquor.user_id != user_id:
        return None, "You do not have permission to edit this batch."

    try:
        # Validate bottle count
        bottle_count = form_data.get("bottle_count")
        if bottle_count is not None:
            try:
                bottle_count = int(bottle_count)
                if bottle_count < 0:
                    return None, "Bottle count must be non-negative"
            except (ValueError, TypeError):
                return None, "Bottle count must be a valid integer"

        # Validate bottle volume
        bottle_volume = form_data.get("bottle_volume")
        if bottle_volume is not None:
            try:
                bottle_volume = float(bottle_volume)
                if bottle_volume < 0:
                    return None, "Bottle volume must be non-negative"
            except (ValueError, TypeError):
                return None, "Bottle volume must be a valid number"

        # Update batch fields
        if bottle_count is not None:
            batch.bottle_count = bottle_count

        if bottle_volume is not None:
            bottle_volume_ml: float = bottle_volume
            if form_data.get("bottle_volume_unit") == "l":
                bottle_volume_ml *= 1000
            batch.bottle_volume = bottle_volume_ml
            batch.bottle_volume_unit = "ml"

        batch_repository.commit()
        return batch, None
    except Exception as e:
        batch_repository.rollback()
        return None, f"An unexpected error occurred: {str(e)}"


def generate_api_key() -> str:
    """Generate a secure API key"""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(32))


def create_api_key(user_id: int, name: str) -> Tuple[Optional[ApiKey], Optional[str]]:
    """
    Service to create a new API key for a user.
    Returns (api_key_object, None) on success or (None, error_message) on failure.
    """
    try:
        key = generate_api_key()
        api_key = ApiKey(user_id=user_id, key=key, name=name)
        api_key_repository.add(api_key)
        api_key_repository.commit()
        return api_key, None
    except Exception as e:
        api_key_repository.rollback()
        return None, f"An unexpected error occurred: {str(e)}"


def get_api_keys_for_user(user_id: int) -> List[ApiKey]:
    """Service to get all API keys for a user"""
    return api_key_repository.get_all_for_user(user_id)


def get_paginated_api_keys_for_user(
    user_id: int, page: int = 1, per_page: int = 10
) -> Tuple[List[ApiKey], int]:
    """Service to get paginated API keys for a user"""
    return api_key_repository.get_paginated_for_user(user_id, page, per_page)


def get_api_key_by_id_and_user(api_key_id: int, user_id: int) -> Optional[ApiKey]:
    """Service to get an API key by ID for a specific user"""
    return api_key_repository.get_by_id_and_user(api_key_id, user_id)


def delete_api_key(api_key_id: int, user_id: int) -> Tuple[bool, Optional[str]]:
    """
    Service to delete an API key.
    Returns (True, None) on success or (False, error_message) on failure.
    """
    try:
        api_key = api_key_repository.get_by_id_and_user(api_key_id, user_id)
        if not api_key:
            return False, "API key not found."

        api_key_repository.delete(api_key)
        return True, None
    except Exception as e:
        return False, f"An unexpected error occurred: {str(e)}"


def get_liquors_for_user(user_id: int) -> List[Liquor]:
    """Service to get all liquors for a user"""
    return liquor_repository.get_all_for_user(user_id)


def get_paginated_liquors_for_user(
    user_id: int, page: int = 1, per_page: int = 10
) -> Tuple[List[Liquor], int]:
    """Service to get paginated liquors for a user"""
    return liquor_repository.get_paginated_for_user(user_id, page, per_page)


def create_liquor(user_id: int, name: str, description: Optional[str] = None) -> Liquor:
    """Service to create a new liquor"""
    # Validate name
    if not name or not name.strip():
        raise ValueError("Liquor name cannot be empty")

    # Check if liquor with this name already exists for this user
    existing_liquor = (
        db.session.query(Liquor).filter_by(user_id=user_id, name=name).first()
    )
    if existing_liquor:
        raise ValueError("Liquor with this name already exists for this user")

    return liquor_repository.create(
        name=name.strip(), user_id=user_id, description=description
    )


def get_liquor_by_id(liquor_id: int, user_id: int) -> Optional[Liquor]:
    """Service to get a liquor by ID for a specific user"""
    return liquor_repository.get_by_id_and_user(liquor_id, user_id)


def update_liquor(
    liquor_id: int, user_id: int, data: Dict[str, Any]
) -> Optional[Liquor]:
    """Service to update a liquor"""
    liquor = get_liquor_by_id(liquor_id, user_id)
    if not liquor:
        return None

    # Validate name if provided
    if "name" in data:
        name = data["name"]
        if not name or not name.strip():
            raise ValueError("Liquor name cannot be empty")

        # Check if liquor with this name already exists for this user.
        existing_liquor = (
            db.session.query(Liquor)
            .filter(
                Liquor.user_id == user_id,
                Liquor.name == name,
                Liquor.id != liquor_id,
            )
            .first()
        )
        if existing_liquor:
            raise ValueError("Liquor with this name already exists for this user")

    liquor_repository.update(liquor, data)
    return liquor


def delete_liquor(liquor_id: int, user_id: int) -> bool:
    """Service to delete a liquor"""
    liquor = get_liquor_by_id(liquor_id, user_id)
    if not liquor:
        return False

    liquor_repository.delete(liquor)
    return True


def get_all_ingredients() -> List[Ingredient]:
    """Service to get all ingredients"""
    return ingredient_repository.get_all()


def create_ingredient(name: str, description: Optional[str] = None) -> Ingredient:
    """Service to create a new ingredient"""
    # Validate name
    if not name or not name.strip():
        raise ValueError("Ingredient name cannot be empty")

    # Check if ingredient with this name already exists
    existing_ingredient = ingredient_repository.get_by_name(name)
    if existing_ingredient:
        raise ValueError("Ingredient with this name already exists")

    return ingredient_repository.create(name=name.strip(), description=description)


def get_ingredient_by_id(ingredient_id: int) -> Optional[Ingredient]:
    """Service to get an ingredient by ID"""
    return ingredient_repository.get(ingredient_id)


def update_ingredient(ingredient_id: int, data: Dict[str, Any]) -> Optional[Ingredient]:
    """Service to update an ingredient"""
    ingredient = get_ingredient_by_id(ingredient_id)
    if not ingredient:
        return None

    # Validate name if provided
    if "name" in data:
        name = data["name"]
        if not name or not name.strip():
            raise ValueError("Ingredient name cannot be empty")

        # Check if ingredient with this name already exists.
        existing_ingredient = ingredient_repository.get_by_name(name)
        if existing_ingredient and existing_ingredient.id != ingredient_id:
            raise ValueError("Ingredient with this name already exists")

    ingredient_repository.update(ingredient, data)
    return ingredient


def delete_ingredient(ingredient_id: int) -> bool:
    """Service to delete an ingredient"""
    ingredient = get_ingredient_by_id(ingredient_id)
    if not ingredient:
        return False

    ingredient_repository.delete(ingredient)
    return True


def get_batches_for_liquor(liquor_id: int) -> List[Batch]:
    """Service to get all batches for a liquor"""
    return batch_repository.get_all_for_liquor(liquor_id)


def get_paginated_batches_for_liquor(
    liquor_id: int, page: int = 1, per_page: int = 10
) -> Tuple[List[Batch], int]:
    """Service to get paginated batches for a liquor"""
    return batch_repository.get_paginated_for_liquor(liquor_id, page, per_page)


def create_batch(batch_data: dict) -> Tuple[Optional[Batch], Optional[str]]:
    """Service to create a new batch"""
    # Validate required fields
    if "liquor_id" not in batch_data:
        return None, "Liquor ID is required"

    # Validate numeric fields
    if "bottle_count" in batch_data:
        try:
            bottle_count = int(batch_data["bottle_count"])
            if bottle_count < 0:
                return None, "Bottle count must be non-negative"
        except (ValueError, TypeError):
            return None, "Bottle count must be a valid integer"

    if "bottle_volume" in batch_data:
        try:
            bottle_volume = float(batch_data["bottle_volume"])
            if bottle_volume < 0:
                return None, "Bottle volume must be non-negative"
        except (ValueError, TypeError):
            return None, "Bottle volume must be a valid number"

    return batch_repository.create(batch_data)


def get_batch_by_id(batch_id: int) -> Optional[Batch]:
    """Service to get a batch by ID"""
    return batch_repository.get(batch_id)


def update_batch(batch_id: int, data: Dict[str, Any]) -> Optional[Batch]:
    """Service to update a batch"""
    batch = get_batch_by_id(batch_id)
    if not batch:
        return None

    # Validate numeric fields if provided
    if "bottle_count" in data:
        try:
            bottle_count = int(data["bottle_count"])
            if bottle_count < 0:
                raise ValueError("Bottle count must be non-negative")
        except (ValueError, TypeError):
            raise ValueError("Bottle count must be a valid integer")

    if "bottle_volume" in data:
        try:
            bottle_volume = float(data["bottle_volume"])
            if bottle_volume < 0:
                raise ValueError("Bottle volume must be non-negative")
        except (ValueError, TypeError):
            raise ValueError("Bottle volume must be a valid number")

    batch_repository.update(batch, data)
    return batch


def delete_batch(batch_id: int) -> bool:
    """Service to delete a batch"""
    batch = get_batch_by_id(batch_id)
    if not batch:
        return False

    batch_repository.delete(batch)
    return True


def get_formulas_for_batch(batch_id: int) -> List[BatchFormula]:
    """Service to get all formulas for a batch"""
    return batch_formula_repository.get_all_for_batch(batch_id)


def get_paginated_formulas_for_batch(
    batch_id: int, page: int = 1, per_page: int = 10
) -> Tuple[List[BatchFormula], int]:
    """Service to get paginated formulas for a batch"""
    return batch_formula_repository.get_paginated_for_batch(batch_id, page, per_page)


def create_batch_formula(
    batch_id: int, ingredient_id: int, quantity: float, unit: str
) -> Tuple[Optional[BatchFormula], Optional[str]]:
    """Service to create a new formula for a batch"""
    # First check if the batch exists
    batch = get_batch_by_id(batch_id)
    if not batch:
        return None, "Batch not found."

    # Check if the ingredient exists
    ingredient = get_ingredient_by_id(ingredient_id)
    if not ingredient:
        return None, "Ingredient not found."

    # Validate quantity
    if quantity <= 0:
        return None, f"Quantity must be positive, got {quantity}"

    return batch_formula_repository.create(batch_id, ingredient_id, quantity, unit)


def get_batch_formula_by_id(formula_id: int) -> Optional[BatchFormula]:
    """Service to get a batch formula by ID"""
    return batch_formula_repository.get(formula_id)


def update_batch_formula(
    formula_id: int, data: Dict[str, Any]
) -> Tuple[Optional[BatchFormula], Optional[str]]:
    """Service to update a batch formula"""
    formula = get_batch_formula_by_id(formula_id)
    if not formula:
        return None, "Formula not found."

    # Validate ingredient if provided
    if "ingredient_id" in data:
        ingredient = get_ingredient_by_id(data["ingredient_id"])
        if not ingredient:
            return None, "Ingredient not found."

    # Validate quantity if provided
    if "quantity" in data:
        try:
            quantity = float(data["quantity"])
            if quantity <= 0:
                return None, f"Quantity must be positive, got {quantity}"
        except (ValueError, TypeError):
            return None, "Quantity must be a valid number"

    return batch_formula_repository.update(formula, data)


def delete_batch_formula(formula_id: int) -> bool:
    """Service to delete a batch formula"""
    formula = get_batch_formula_by_id(formula_id)
    if not formula:
        return False

    return batch_formula_repository.delete(formula)
