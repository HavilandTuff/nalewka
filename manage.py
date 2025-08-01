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
        Liquor(name='Wiśniówka', description='Traditional Polish cherry liqueur made with fresh cherries and vodka', user_id=user.id),
        Liquor(name='Cytrynówka', description='Refreshing lemon liqueur with citrus zest and honey', user_id=user.id),
        Liquor(name='Nalewka z Malin', description='Sweet raspberry liqueur perfect for desserts', user_id=user.id),
        Liquor(name='Jagodówka', description='Wild blueberry liqueur with natural sweetness', user_id=user.id),
        Liquor(name='Śliwówka', description='Plum liqueur aged for rich flavor', user_id=user.id)
    ]
    
    for liquor in liquors:
        db.session.add(liquor)
    db.session.flush()
    
    # Create sample ingredients
    ingredients = [
        Ingredient(name='Cherries', description='Fresh cherries for liqueur making'),
        Ingredient(name='Lemons', description='Fresh lemons with zest for citrus flavor'),
        Ingredient(name='Raspberries', description='Fresh raspberries for berry liqueurs'),
        Ingredient(name='Blueberries', description='Wild blueberries for natural sweetness'),
        Ingredient(name='Plums', description='Ripe plums for traditional nalewka'),
        Ingredient(name='Sugar', description='Granulated sugar for sweetness'),
        Ingredient(name='Honey', description='Natural honey for complex sweetness'),
        Ingredient(name='Vodka', description='High-quality vodka for base spirit'),
        Ingredient(name='Cinnamon', description='Ground cinnamon for spice'),
        Ingredient(name='Vanilla', description='Vanilla beans for aroma')
    ]
    
    for ingredient in ingredients:
        db.session.add(ingredient)
    db.session.flush()
    
    # Create sample batches
    batches = [
        Batch(description='First batch of Wiśniówka - traditional family recipe', liquor_id=liquors[0].id),
        Batch(description='Summer batch of Cytrynówka with fresh lemons', liquor_id=liquors[1].id),
        Batch(description='Experimental raspberry batch with honey', liquor_id=liquors[2].id)
    ]
    
    for batch in batches:
        db.session.add(batch)
    db.session.flush()
    
    # Create sample batch formulas
    formulas = [
        # Wiśniówka batch
        BatchFormula(batch_id=batches[0].id, ingredient_id=ingredients[0].id, quantity=1000, unit='grams'),
        BatchFormula(batch_id=batches[0].id, ingredient_id=ingredients[5].id, quantity=300, unit='grams'),
        BatchFormula(batch_id=batches[0].id, ingredient_id=ingredients[7].id, quantity=1500, unit='milliliters'),
        
        # Cytrynówka batch
        BatchFormula(batch_id=batches[1].id, ingredient_id=ingredients[1].id, quantity=500, unit='grams'),
        BatchFormula(batch_id=batches[1].id, ingredient_id=ingredients[6].id, quantity=200, unit='grams'),
        BatchFormula(batch_id=batches[1].id, ingredient_id=ingredients[7].id, quantity=1000, unit='milliliters'),
        
        # Raspberry batch
        BatchFormula(batch_id=batches[2].id, ingredient_id=ingredients[2].id, quantity=800, unit='grams'),
        BatchFormula(batch_id=batches[2].id, ingredient_id=ingredients[6].id, quantity=150, unit='grams'),
        BatchFormula(batch_id=batches[2].id, ingredient_id=ingredients[7].id, quantity=1200, unit='milliliters')
    ]
    
    for formula in formulas:
        db.session.add(formula)
    
    try:
        db.session.commit()
        print("✅ Sample data created successfully!")
        print(f"👤 User: admin / password123")
        print(f"🍷 Created {len(liquors)} liquors")
        print(f"🥄 Created {len(ingredients)} ingredients")
        print(f"📦 Created {len(batches)} batches")
        print(f"📝 Created {len(formulas)} batch formulas")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating sample data: {e}")


def reset_database():
    """Reset the database and create tables."""
    print("🔄 Resetting database...")
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("✅ Database reset complete!")


def init_db():
    """Initialize the database."""
    print("🚀 Initializing database...")
    with app.app_context():
        db.create_all()
        print("✅ Database initialized!")


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