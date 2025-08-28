from app import db
from app.models import Batch, BatchFormula, Liquor


def create_batch_with_ingredients(form_data, liquor_id, user_id):
    """
    Service to create a batch and its ingredient formulas.
    Returns (batch_object, None) on success or (None, error_message) on failure.
    """
    # Verify the liquor belongs to the user
    liquor = db.session.get(Liquor, liquor_id)
    if not liquor or liquor.user_id != user_id:
        return None, "Liquor not found or access denied."

    try:
        bottle_volume_ml = form_data.get("bottle_volume") or 0
        if form_data.get("bottle_volume_unit") == "l" and bottle_volume_ml > 0:
            bottle_volume_ml *= 1000

        new_batch = Batch(
            description=form_data["batch_description"],
            liquor_id=liquor_id,
            bottle_count=form_data.get("bottle_count") or 0,
            bottle_volume=bottle_volume_ml,
            bottle_volume_unit="ml",
        )
        db.session.add(new_batch)
        db.session.flush()  # Get the new_batch.id

        ingredients_added = 0
        for ing_data in form_data.get("ingredients", []):
            if (
                ing_data.get("ingredient")
                and ing_data.get("quantity")
                and ing_data.get("unit")
            ):
                formula = BatchFormula(
                    batch_id=new_batch.id,
                    ingredient_id=ing_data["ingredient"],
                    quantity=float(ing_data["quantity"]),
                    unit=ing_data["unit"],
                )
                db.session.add(formula)
                ingredients_added += 1

        if ingredients_added == 0:
            db.session.rollback()
            return None, "At least one valid ingredient must be added."

        db.session.commit()
        return new_batch, None
    except Exception as e:
        db.session.rollback()
        return None, f"An unexpected error occurred: {str(e)}"


def update_batch_bottles(batch_id, user_id, form_data):
    """
    Service to update the bottle information for a batch.
    Returns (batch_object, None) on success or (None, error_message) on failure.
    """
    batch = db.session.get(Batch, batch_id)
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

        db.session.commit()
        return batch, None
    except Exception as e:
        db.session.rollback()
        return None, f"An unexpected error occurred: {str(e)}"
