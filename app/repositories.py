from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, cast

import sqlalchemy as sa
from sqlalchemy.orm import joinedload

from app import db
from app.models import ApiKey, Batch, BatchFormula, Ingredient, Liquor, User

T = TypeVar("T")


class BaseRepository:
    def __init__(self, model: Type[T]) -> None:
        self.model = model

    def get(self, model_id: int) -> Optional[T]:
        result = db.session.get(self.model, model_id)
        return cast(Optional[T], result)

    def add(self, entity: T) -> None:
        db.session.add(entity)

    def commit(self) -> None:
        db.session.commit()

    def rollback(self) -> None:
        db.session.rollback()

    def flush(self) -> None:
        db.session.flush()


class ApiKeyRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(ApiKey)

    def get_by_key(self, key: str) -> Optional[ApiKey]:
        result = db.session.scalar(db.select(ApiKey).where(ApiKey.key == key))
        return cast(Optional[ApiKey], result)

    def get_all_for_user(self, user_id: int) -> List[ApiKey]:
        result = db.session.scalars(
            db.select(ApiKey).where(ApiKey.user_id == user_id)
        ).all()
        return list(result)

    def get_by_id_and_user(self, api_key_id: int, user_id: int) -> Optional[ApiKey]:
        result = db.session.scalar(
            db.select(ApiKey).where(ApiKey.id == api_key_id, ApiKey.user_id == user_id)
        )
        return cast(Optional[ApiKey], result)

    def delete(self, api_key: ApiKey) -> None:
        db.session.delete(api_key)
        db.session.commit()


class LiquorRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(Liquor)

    def get_all_for_user(self, user_id: int) -> List[Liquor]:
        result = db.session.scalars(
            db.select(Liquor).where(Liquor.user_id == user_id)
        ).all()
        return list(result)

    def user_owns_liquor(self, liquor_id: int, user_id: int) -> bool:
        return (
            db.session.query(Liquor.id).filter_by(id=liquor_id, user_id=user_id).first()
            is not None
        )

    def create(
        self, name: str, user_id: int, description: Optional[str] = None
    ) -> Liquor:
        liquor = Liquor(name=name, user_id=user_id, description=description)
        self.add(liquor)
        self.commit()
        return liquor

    def get_by_id_and_user(self, liquor_id: int, user_id: int) -> Optional[Liquor]:
        result = db.session.scalar(
            db.select(Liquor).where(Liquor.id == liquor_id, Liquor.user_id == user_id)
        )
        return cast(Optional[Liquor], result)

    def update(self, liquor: Liquor, data: Dict[str, Any]) -> None:
        for key, value in data.items():
            setattr(liquor, key, value)
        self.commit()

    def delete(self, liquor: Liquor) -> None:
        db.session.delete(liquor)
        db.session.commit()


class BatchRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(Batch)

    def get(self, model_id: int) -> Optional[Batch]:
        result = (
            db.session.query(Batch)
            .options(
                joinedload(Batch.formulas).joinedload(BatchFormula.ingredient),
                joinedload(Batch.liquor),
            )
            .filter(Batch.id == model_id)
            .first()
        )
        return cast(Optional[Batch], result)

    def get_all_for_liquor(self, liquor_id: int) -> List[Batch]:
        result = db.session.scalars(
            db.select(Batch)
            .where(Batch.liquor_id == liquor_id)
            .order_by(Batch.date.desc())
        ).all()
        return list(result)

    def create_with_formulas(
        self, batch_data: dict, formulas_data: List[dict]
    ) -> Tuple[Optional[Batch], Optional[str]]:
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
    def __init__(self) -> None:
        super().__init__(User)

    def get_by_username(self, username: str) -> Optional[User]:
        result = db.session.scalar(db.select(User).where(User.username == username))
        return cast(Optional[User], result)

    def get_by_email(self, email: str) -> Optional[User]:
        result = db.session.scalar(db.select(User).where(User.email == email))
        return cast(Optional[User], result)


class IngredientRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(Ingredient)

    def get_all(self) -> List[Ingredient]:
        result = db.session.scalars(sa.select(Ingredient)).all()
        return list(result)

    def get_by_name(self, name: str) -> Optional[Ingredient]:
        result = db.session.scalar(db.select(Ingredient).where(Ingredient.name == name))
        return cast(Optional[Ingredient], result)

    def create(self, name: str, description: Optional[str] = None) -> Ingredient:
        ingredient = Ingredient(name=name, description=description)
        self.add(ingredient)
        self.commit()
        return ingredient

    def get(self, ingredient_id: int) -> Optional[Ingredient]:
        result = db.session.get(Ingredient, ingredient_id)
        return cast(Optional[Ingredient], result)

    def update(self, ingredient: Ingredient, data: Dict[str, Any]) -> None:
        for key, value in data.items():
            setattr(ingredient, key, value)
        self.commit()

    def delete(self, ingredient: Ingredient) -> None:
        db.session.delete(ingredient)
        db.session.commit()
