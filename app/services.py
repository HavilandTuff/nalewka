from app.repositories import BatchRepository, LiquorRepository

liquor_repository = LiquorRepository()
batch_repository = BatchRepository()


def create_batch_with_ingredients(form_data, liquor_id, user_id):
    """
    Service to create a batch and its ingredient formulas.
    Returns (batch_object, None) on success or (None, error_message) on failure.
    """
    liquor = liquor_repository.get(liquor_id)
    if not liquor or liquor.user_id != user_id:
        return None, "Liquor not found or access denied."

    try:
        bottle_volume_ml = form_data.get("bottle_volume") or 0
        if form_data.get("bottle_volume_unit") == "l" and bottle_volume_ml > 0:
            bottle_volume_ml *= 1000

        batch_data = {
            "description": form_data["batch_description"],
            "liquor_id": liquor_id,
            "bottle_count": form_data.get("bottle_count") or 0,
            "bottle_volume": bottle_volume_ml,
            "bottle_volume_unit": "ml",
        }

        formulas_data = []
        for ing_data in form_data.get("ingredients", []):
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


def update_batch_bottles(batch_id, user_id, form_data):
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
        bottle_volume_ml = form_data["bottle_volume"]
        if form_data["bottle_volume_unit"] == "l":
            bottle_volume_ml *= 1000

        batch.bottle_count = form_data["bottle_count"]
        batch.bottle_volume = bottle_volume_ml
        batch.bottle_volume_unit = "ml"

        batch_repository.commit()
        return batch, None
    except Exception as e:
        batch_repository.rollback()
        return None, f"An unexpected error occurred: {str(e)}"
