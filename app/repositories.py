from .models import Batch, Liquor


class LiquorRepository:
    """Handles data access for Liquor models."""

    def get_by_id(self, liquor_id):
        return Liquor.query.get(liquor_id)

    def get_all(self):
        return Liquor.query.order_by(Liquor.name).all()


class BatchRepository:
    """Handles data access for Batch models."""

    def get_for_liquor(self, liquor_id):
        return (
            Batch.query.filter_by(liquor_id=liquor_id).order_by(Batch.date.desc()).all()
        )

    def get_by_id(self, batch_id):
        return Batch.query.get(batch_id)


# You would add other repositories here as needed (e.g., IngredientRepository)
