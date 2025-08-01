#!/usr/bin/env python3
"""
Management script for the Nalewka application.
"""
import os
import sys
from app import app, db
from app.models import User, Liquor, Ingredient, Batch, BatchFormula
from werkzeug.security import generate_password_hash


def create_sample_data():
    """Create sample data for testing."""
    print("Creating sample data...")
    
    # Create sample user
    user = User(
        username='admin',
        email='admin@example.com'
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.flush()
    
    # Create sample liquors
    liquors = [
        Liquor(name='Wiśniówka', description='Traditional cherry liqueur', user_id=user.id),
        Liquor(name='Cytrynówka', description='Lemon liqueur', user_id=user.id),
        Liquor(name='Nalewka z Malin', description='Raspberry liqueur', user_id=user.id)
    ]
    
    for liquor in liquors:
        db.session.add(liquor)
    db.session.flush()
    
    # Create sample ingredients
    ingredients = [
        Ingredient(name='Cherries', description='Fresh cherries for liqueur'),
        Ingredient(name='Lemons', description='Fresh lemons with zest'),
        Ingredient(name='Raspberries', description='Fresh raspberries'),
        Ingredient(name='Sugar', description='Granulated sugar'),
        Ingredient(name='Vodka', description='High-quality vodka for base'),
        Ingredient(name='Honey', description='Natural honey for sweetness')
    ]
    
    for ingredient in ingredients:
        db.session.add(ingredient)
    db.session.flush()
    
    # Create sample batch
    batch = Batch(
        description='First batch of Wiśniówka - traditional recipe',
        liquor_id=liquors[0].id
    )
    db.session.add(batch)
    db.session.flush()
    
    # Create sample batch formulas
    formulas = [
        BatchFormula(batch_id=batch.id, ingredient_id=ingredients[0].id, quantity=500, unit='grams'),
        BatchFormula(batch_id=batch.id, ingredient_id=ingredients[3].id, quantity=200, unit='grams'),
        BatchFormula(batch_id=batch.id, ingredient_id=ingredients[4].id, quantity=1000, unit='milliliters')
    ]
    
    for formula in formulas:
        db.session.add(formula)
    
    try:
        db.session.commit()
        print("Sample data created successfully!")
        print(f"User: admin / password123")
        print(f"Created {len(liquors)} liquors, {len(ingredients)} ingredients, and 1 batch")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating sample data: {e}")


def reset_database():
    """Reset the database and create tables."""
    print("Resetting database...")
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database reset complete!")


def init_db():
    """Initialize the database."""
    print("Initializing database...")
    with app.app_context():
        db.create_all()
        print("Database initialized!")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python manage.py [init|reset|sample]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'init':
        init_db()
    elif command == 'reset':
        reset_database()
    elif command == 'sample':
        with app.app_context():
            create_sample_data()
    else:
        print("Unknown command. Use: init, reset, or sample")
        sys.exit(1) 