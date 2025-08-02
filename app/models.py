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

    liquors: so.Mapped[list['Liquor']] = so.relationship(back_populates='author')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
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


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Ingredient(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True, unique=True)
    description: so.Mapped[str] = so.mapped_column(sa.Text())

    # Relationship to BatchFormula
    batch_formulas: so.Mapped[list['BatchFormula']] = so.relationship(back_populates='ingredient')

    def __repr__(self):
        return f'<Ingredient {self.name}>'


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

    def __repr__(self):
        return f'<Batch {self.id} - {self.description[:50]}...>'
    
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
