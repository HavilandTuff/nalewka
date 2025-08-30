import sqlalchemy as sa

from app import db
from app.models import Batch, BatchFormula, Ingredient, Liquor, User


class BaseRepository:
    def __init__(self, model):
        self.model = model

    def get(self, model_id):
        return db.session.get(self.model, model_id)

    def add(self, entity):
        db.session.add(entity)

    def commit(self):
        db.session.commit()

    def rollback(self):
        db.session.rollback()

    def flush(self):
        db.session.flush()


class LiquorRepository(BaseRepository):
    def __init__(self):
        super().__init__(Liquor)

    def get_all_for_user(self, user_id):
        return db.session.scalars(
            db.select(Liquor).where(Liquor.user_id == user_id)
        ).all()

    def user_owns_liquor(self, liquor_id, user_id):
        return (
            db.session.query(Liquor.id).filter_by(id=liquor_id, user_id=user_id).first()
            is not None
        )


class BatchRepository(BaseRepository):
    def __init__(self):
        super().__init__(Batch)

    def get_all_for_liquor(self, liquor_id):
        return db.session.scalars(
            db.select(Batch)
            .where(Batch.liquor_id == liquor_id)
            .order_by(Batch.date.desc())
        ).all()

    def create_with_formulas(self, batch_data, formulas_data):
        try:
            batch = Batch(**batch_data)
            batch.validate_bottle_data()
            self.add(batch)
            self.flush()

            for formula_data in formulas_data:
                formula = BatchFormula(batch_id=batch.id, **formula_data)
                self.add(formula)

            self.commit()
            return batch, None
        except Exception as e:
            self.rollback()
            return None, str(e)


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def get_by_username(self, username):
        return db.session.scalar(db.select(User).where(User.username == username))

    def get_by_email(self, email):
        return db.session.scalar(db.select(User).where(User.email == email))


class IngredientRepository(BaseRepository):
    def __init__(self):
        super().__init__(Ingredient)

    def get_all(self):
        return db.session.scalars(sa.select(Ingredient)).all()
