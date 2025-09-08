import secrets
import string
from typing import Any, Dict, List, Optional, Tuple, Union

from app.models import ApiKey, Batch, Liquor
from app.repositories import ApiKeyRepository, BatchRepository, LiquorRepository

liquor_repository = LiquorRepository()
batch_repository = BatchRepository()
api_key_repository = ApiKeyRepository()


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
                formulas_data.append(
                    {
                        "ingredient_id": ing_data["ingredient"],
                        "quantity": float(ing_data["quantity"]),
                        "unit": ing_data["unit"],
                    }
                )

        if not formulas_data:
            return None, "At least one valid ingredient must be added."

        return batch_repository.create_with_formulas(batch_data, formulas_data)
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
        bottle_volume_ml: float = form_data["bottle_volume"]  # type: ignore
        if form_data["bottle_volume_unit"] == "l":  # type: ignore
            bottle_volume_ml *= 1000

        batch.bottle_count = form_data["bottle_count"]  # type: ignore
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


def create_liquor(user_id: int, name: str, description: Optional[str] = None) -> Liquor:
    """Service to create a new liquor"""
    return liquor_repository.create(name=name, user_id=user_id, description=description)


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

    liquor_repository.update(liquor, data)
    return liquor


def delete_liquor(liquor_id: int, user_id: int) -> bool:
    """Service to delete a liquor"""
    liquor = get_liquor_by_id(liquor_id, user_id)
    if not liquor:
        return False

    liquor_repository.delete(liquor)
    return True
