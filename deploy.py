#!/usr/bin/env python3
"""
Deployment script for Render.
This script handles database migrations and optionally creates sample data.
"""
import os
import sys
from typing import List

# Ensure we're using the correct path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Batch, BatchFormula, Ingredient, Liquor, User


def init_database() -> None:
    """Initialize the database tables."""
    print("Running database migrations...")
    # Create app with proper configuration
    app = create_app()
    with app.app_context():
        # Use Flask-Migrate to run migrations
        from flask_migrate import upgrade

        upgrade()
        print("✅ Database migrations completed successfully!")


def create_sample_data() -> bool:
    """Create sample data for the application.

    Returns:
        bool: True if sample data was created, False if it was skipped.
    """
    print("Checking for existing data...")

    # Create app with proper configuration
    app = create_app()
    with app.app_context():
        # Check if any user already exists
        existing_user = User.query.first()
        if existing_user:
            print("Existing data found, skipping sample data creation.")
            return False

        print("Creating sample data...")

        # Create admin user
        admin_user = User(username="admin", email="admin@example.com")
        admin_user.set_password("password123")
        db.session.add(admin_user)
        db.session.flush()

        # Create sample liquors
        liquors: List[Liquor] = [
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
        ingredients: List[Ingredient] = [
            Ingredient(
                name="Cherries", description="Fresh cherries for liqueur making"
            ),
            Ingredient(
                name="Lemons", description="Fresh lemons with zest for citrus flavor"
            ),
            Ingredient(
                name="Raspberries", description="Fresh raspberries for berry liquors"
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
        formulas: List[BatchFormula] = [
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
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating sample data: {e}")
            return False


def main() -> None:
    """Main deployment function."""
    init_database()

    # Check if we should create sample data
    if len(sys.argv) > 1 and sys.argv[1] == "--sample":
        create_sample_data()
    elif len(sys.argv) > 1 and sys.argv[1] == "--force-sample":
        # Force creation of sample data regardless of existing data
        print("Force creating sample data...")
        create_sample_data()
    else:
        print("Skipping sample data creation. Use --sample to create sample data.")


if __name__ == "__main__":
    main()
