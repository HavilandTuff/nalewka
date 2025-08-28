#!/usr/bin/env python3
"""
Deployment script for Render.
This script initializes the database and creates sample data.
"""
import sys

from app import app, db
from app.models import Batch, BatchFormula, Ingredient, Liquor, User


def init_database():
    """Initialize the database tables."""
    print("Creating database tables...")
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")


def create_sample_data():
    """Create sample data for the application."""
    print("Creating sample data...")

    with app.app_context():
        # Check if admin user already exists
        admin_user = User.query.filter_by(username="admin").first()
        if admin_user:
            print("Admin user already exists, skipping sample data creation.")
            return

        # Create admin user
        admin_user = User(username="admin", email="admin@example.com")
        admin_user.set_password("password123")
        db.session.add(admin_user)
        db.session.flush()

        # Create sample liquors
        liquors = [
            Liquor(
                name="Wiśniówka",
                description=(
                    "Traditional Polish cherry liqueur made with fresh "
                    "cherries and vodka"
                ),
                user_id=admin_user.id,
            ),
            Liquor(
                name="Cytrynówka",
                description="Refreshing lemon liqueur with citrus zest and honey",
                user_id=admin_user.id,
            ),
            Liquor(
                name="Nalewka z Malin",
                description="Sweet raspberry liqueur perfect for desserts",
                user_id=admin_user.id,
            ),
        ]

        for liquor in liquors:
            db.session.add(liquor)
        db.session.flush()

        # Create sample ingredients
        ingredients = [
            Ingredient(
                name="Cherries", description="Fresh cherries for liqueur making"
            ),
            Ingredient(
                name="Lemons", description="Fresh lemons with zest for citrus flavor"
            ),
            Ingredient(
                name="Raspberries", description="Fresh raspberries for berry liqueurs"
            ),
            Ingredient(name="Sugar", description="Granulated sugar for sweetness"),
            Ingredient(name="Honey", description="Natural honey for complex sweetness"),
            Ingredient(name="Vodka", description="High-quality vodka for base spirit"),
        ]

        for ingredient in ingredients:
            db.session.add(ingredient)
        db.session.flush()

        # Create sample batch
        batch = Batch(
            description="First batch of Wiśniówka - traditional family recipe",
            liquor_id=liquors[0].id,
        )
        db.session.add(batch)
        db.session.flush()

        # Create sample batch formulas
        formulas = [
            BatchFormula(
                batch_id=batch.id,
                ingredient_id=ingredients[0].id,
                quantity=1000,
                unit="grams",
            ),
            BatchFormula(
                batch_id=batch.id,
                ingredient_id=ingredients[3].id,
                quantity=300,
                unit="grams",
            ),
            BatchFormula(
                batch_id=batch.id,
                ingredient_id=ingredients[5].id,
                quantity=1500,
                unit="milliliters",
            ),
        ]

        for formula in formulas:
            db.session.add(formula)

        try:
            db.session.commit()
            print("✅ Sample data created successfully!")
            print("👤 Admin user: admin / password123")
            print(f"🍷 Created {len(liquors)} liquors")
            print(f"🥄 Created {len(ingredients)} ingredients")
            print(f"📦 Created 1 batch with {len(formulas)} formulas")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating sample data: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--sample":
        init_database()
        create_sample_data()
    else:
        init_database()
