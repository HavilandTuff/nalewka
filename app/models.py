from datetime import datetime, timezone
from typing import Optional, TypeAlias

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login
from app.utils import VolumeConverter

BaseModel: TypeAlias = db.Model


class User(UserMixin, BaseModel):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    created_at: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )

    liquors: so.Mapped[list["Liquor"]] = so.relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"<User {self.username}>"

    def set_password(self, password: str) -> None:
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)


class Liquor(BaseModel):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    created: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.Text())
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    user: so.Mapped[User] = so.relationship(back_populates="liquors")
    batches: so.Mapped[list["Batch"]] = so.relationship(
        back_populates="liquor", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Liquor {self.name}>"

    @property
    def batch_count(self) -> int:
        """Return the number of batches for this liquor"""
        return len(self.batches)

    @property
    def total_bottles_produced(self) -> int:
        """Calculate total bottles produced across all batches"""
        return sum(batch.bottle_count or 0 for batch in self.batches)

    @property
    def total_volume_produced(self) -> float:
        """Calculate total volume produced in milliliters"""
        return sum(batch.total_volume for batch in self.batches)


@login.user_loader
def load_user(id: int) -> Optional["User"]:
    return db.session.get(User, int(id))


class Ingredient(BaseModel):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True, unique=True)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.Text())
    created_at: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )

    # Relationship to BatchFormula
    batch_formulas: so.Mapped[list["BatchFormula"]] = so.relationship(
        back_populates="ingredient"
    )

    def __repr__(self) -> str:
        return f"<Ingredient {self.name}>"

    @property
    def usage_count(self) -> int:
        """Return how many batches use this ingredient"""
        return len(self.batch_formulas)


class Batch(BaseModel):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    date: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    description: so.Mapped[str] = so.mapped_column(sa.Text())
    liquor_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Liquor.id), index=True)

    # Bottle tracking fields
    bottle_count: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer(), default=0)
    bottle_volume: so.Mapped[Optional[float]] = so.mapped_column(
        sa.Float(), default=0.0
    )  # in milliliters
    bottle_volume_unit: so.Mapped[str] = so.mapped_column(sa.String(10), default="ml")

    liquor: so.Mapped[Liquor] = so.relationship(back_populates="batches")
    formulas: so.Mapped[list["BatchFormula"]] = so.relationship(
        back_populates="batch", cascade="all, delete-orphan"
    )

    # Add composite index for better query performance
    __table_args__ = (db.Index("idx_batch_liquor_date", "liquor_id", "date"),)

    def __repr__(self) -> str:
        return f"<Batch {self.id} - {self.description[:50]}...>"

    def validate_bottle_data(self) -> None:
        """Validate bottle count and volume are consistent"""
        if self.bottle_count is not None and self.bottle_count < 0:
            raise ValueError("Bottle count cannot be negative")
        if self.bottle_volume is not None and self.bottle_volume < 0:
            raise ValueError("Bottle volume cannot be negative")

    @property
    def total_volume(self) -> float:
        """Calculate total volume in milliliters."""
        if self.bottle_count and self.bottle_volume:
            return self.bottle_count * self.bottle_volume
        return 0.0

    @property
    def total_volume_liters(self) -> float:
        """Calculate total volume in liters."""
        return self.total_volume / 1000.0

    @property
    def ingredient_count(self) -> int:
        """Return the number of ingredients in this batch"""
        return len(self.formulas)

    def get_volume_in_unit(self, unit: str = "ml") -> float:
        """Get total volume in specified unit"""
        total_ml = self.total_volume
        return VolumeConverter.from_ml(total_ml, unit)


class BatchFormula(BaseModel):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    batch_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Batch.id), index=True)
    ingredient_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(Ingredient.id), index=True
    )
    quantity: so.Mapped[float] = so.mapped_column(sa.Float())
    unit: so.Mapped[str] = so.mapped_column(sa.String(20))

    batch: so.Mapped[Batch] = so.relationship(back_populates="formulas")
    ingredient: so.Mapped[Ingredient] = so.relationship(back_populates="batch_formulas")

    def __repr__(self) -> str:
        return f"<BatchFormula {self.ingredient.name}: {self.quantity} {self.unit}>"

    def validate_quantity(self) -> None:
        """Validate that quantity is positive"""
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

    def get_quantity_in_unit(self, target_unit: str) -> float:
        """Convert quantity to target unit (for volume units)"""
        if self.unit in ["ml", "l", "oz", "cup", "tsp", "tbsp"] and target_unit in [
            "ml",
            "l",
            "oz",
            "cup",
            "tsp",
            "tbsp",
        ]:
            ml_value = VolumeConverter.to_ml(self.quantity, self.unit)
            return VolumeConverter.from_ml(ml_value, target_unit)
        return self.quantity  # Return as-is for non-volume units
