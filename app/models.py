from typing import Optional
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from app import db, login


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                             unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    created_at: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))

    liquors: so.Mapped[list['Liquor']] = so.relationship(back_populates='author')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)


class Liquor(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    created: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.Text())
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates='liquors')
    batches: so.Mapped[list['Batch']] = so.relationship(back_populates='liquor', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Liquor {self.name}>'

    @property
    def batch_count(self):
        """Return the number of batches for this liquor"""
        return len(self.batches)

    @property
    def total_bottles_produced(self):
        """Calculate total bottles produced across all batches"""
        return sum(batch.bottle_count or 0 for batch in self.batches)

    @property
    def total_volume_produced(self):
        """Calculate total volume produced in milliliters"""
        return sum(batch.total_volume for batch in self.batches)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Ingredient(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True, unique=True)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.Text())
    created_at: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))

    # Relationship to BatchFormula
    batch_formulas: so.Mapped[list['BatchFormula']] = so.relationship(back_populates='ingredient')

    def __repr__(self):
        return f'<Ingredient {self.name}>'

    @property
    def usage_count(self):
        """Return how many batches use this ingredient"""
        return len(self.batch_formulas)


class VolumeConverter:
    """Utility class for volume conversions"""
    
    @staticmethod
    def to_ml(value, unit):
        """Convert any volume unit to milliliters"""
        if unit == 'l':
            return value * 1000
        elif unit == 'oz':
            return value * 29.5735  # fluid ounces to ml
        elif unit == 'cup':
            return value * 236.588
        elif unit == 'tsp':
            return value * 4.92892
        elif unit == 'tbsp':
            return value * 14.7868
        return value  # assume ml if unknown
    
    @staticmethod
    def from_ml(value_ml, target_unit):
        """Convert milliliters to target unit"""
        if target_unit == 'l':
            return value_ml / 1000
        elif target_unit == 'oz':
            return value_ml / 29.5735
        elif target_unit == 'cup':
            return value_ml / 236.588
        elif target_unit == 'tsp':
            return value_ml / 4.92892
        elif target_unit == 'tbsp':
            return value_ml / 14.7868
        return value_ml  # return ml if unknown


class Batch(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    date: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    description: so.Mapped[str] = so.mapped_column(sa.Text())
    liquor_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Liquor.id), index=True)
    
    # Bottle tracking fields
    bottle_count: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer(), default=0)
    bottle_volume: so.Mapped[Optional[float]] = so.mapped_column(sa.Float(), default=0.0)  # in milliliters
    bottle_volume_unit: so.Mapped[str] = so.mapped_column(sa.String(10), default='ml')

    liquor: so.Mapped[Liquor] = so.relationship(back_populates='batches')
    formulas: so.Mapped[list['BatchFormula']] = so.relationship(back_populates='batch', cascade='all, delete-orphan')

    # Add composite index for better query performance
    __table_args__ = (
        db.Index('idx_batch_liquor_date', 'liquor_id', 'date'),
    )

    def __repr__(self):
        return f'<Batch {self.id} - {self.description[:50]}...>'
    
    def validate_bottle_data(self):
        """Validate bottle count and volume are consistent"""
        if self.bottle_count is not None and self.bottle_count < 0:
            raise ValueError("Bottle count cannot be negative")
        if self.bottle_volume is not None and self.bottle_volume < 0:
            raise ValueError("Bottle volume cannot be negative")
    
    @property
    def total_volume(self):
        """Calculate total volume in milliliters."""
        if self.bottle_count and self.bottle_volume:
            return self.bottle_count * self.bottle_volume
        return 0.0
    
    @property
    def total_volume_liters(self):
        """Calculate total volume in liters."""
        return self.total_volume / 1000.0

    @property
    def ingredient_count(self):
        """Return the number of ingredients in this batch"""
        return len(self.formulas)

    def get_volume_in_unit(self, unit='ml'):
        """Get total volume in specified unit"""
        total_ml = self.total_volume
        return VolumeConverter.from_ml(total_ml, unit)

    @classmethod
    def create_with_formulas(cls, batch_data, formulas_data):
        """Create batch with associated formulas in a transaction"""
        try:
            batch = cls(**batch_data)
            batch.validate_bottle_data()
            db.session.add(batch)
            db.session.flush()
            
            for formula_data in formulas_data:
                formula = BatchFormula(batch_id=batch.id, **formula_data)
                db.session.add(formula)
            
            db.session.commit()
            return batch, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)


class BatchFormula(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    batch_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Batch.id), index=True)
    ingredient_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Ingredient.id), index=True)
    quantity: so.Mapped[float] = so.mapped_column(sa.Float())
    unit: so.Mapped[str] = so.mapped_column(sa.String(20))

    batch: so.Mapped[Batch] = so.relationship(back_populates='formulas')
    ingredient: so.Mapped[Ingredient] = so.relationship(back_populates='batch_formulas')

    def __repr__(self):
        return f'<BatchFormula {self.ingredient.name}: {self.quantity} {self.unit}>'

    def validate_quantity(self):
        """Validate that quantity is positive"""
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than 0")

    def get_quantity_in_unit(self, target_unit):
        """Convert quantity to target unit (for volume units)"""
        if self.unit in ['ml', 'l', 'oz', 'cup', 'tsp', 'tbsp'] and target_unit in ['ml', 'l', 'oz', 'cup', 'tsp', 'tbsp']:
            ml_value = VolumeConverter.to_ml(self.quantity, self.unit)
            return VolumeConverter.from_ml(ml_value, target_unit)
        return self.quantity  # Return as-is for non-volume units
